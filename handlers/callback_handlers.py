from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.enums import ParseMode
from aiogram.utils.keyboard import InlineKeyboardBuilder
import json

from keyboards import Admin_Keyboards, User_Keyboards, Specialist_keyboards
from db_actions import Database
from states import Admin_states, Specialist_states, User_states
from additional_functions import access_block_decorator, fuzzy_handler
from cache_container import cache
from non_script_files.config import QUESTION_PATTERN

db = Database()
router = Router()


@router.callback_query(F.data.contains('district') | F.data.contains('region'))
async def process_miac_selection(callback: types.CallbackQuery, state: FSMContext) -> None:
    '''
    Модуль с выбором МИАЦ
    '''
    if callback.data.startswith('district'):
        district_id = callback.data.split('_')[-1]
        regions_keyboard = await User_Keyboards.create_regions_buttons(district_id=int(district_id))
        await callback.message.edit_text('Выберите регион/область', reply_markup=regions_keyboard)
    elif callback.data.startswith('region'):
        region_id = callback.data.split('_')[-1]
        miac_name = await db.get_miac_information(info_type='miac', miac_id=int(region_id))
        await state.set_state(User_states.reg_fio)
        await state.update_data(subject=miac_name)
        await callback.message.edit_text('Введите ваше ФИО строго через пробел')

@router.callback_query(User_states.fuzzy_process)
async def catch_questions(callback: types.CallbackQuery, state: FSMContext):
    callback_data = callback.data
    
    data = await cache.get(f"questions_pool:{callback.from_user.id}")
    information = json.loads(data)

    if "fuzzy_buttons" in callback_data:
        callback_data = callback_data.split("&") ; callback_data = callback_data[2] ; callback_data = callback_data.split(":") 
        value_id = int(callback_data[1])
        current_question = list(filter(lambda x: value_id == x[0], information))
        current_question = current_question[0][1][1]
        bot_answer, bot_questions = fuzzy_handler(user_question=current_question, pattern=QUESTION_PATTERN)
        await callback.message.edit_text(text=f"Вопрос: {current_question}\nОтвет: {bot_answer}", reply_markup=User_Keyboards.back_to_fuzzy_questions().as_markup())

    elif callback_data == "back_to_fuzzy":
        keyboard, text = User_Keyboards.fuzzy_buttons_generate(information)
        await callback.message.edit_text(text=f"Возможно вы имели в виду:\n{text}", reply_markup=keyboard.as_markup())

@router.callback_query(Specialist_states.choosing_question)
async def process_answers(callback: types.CallbackQuery, state: FSMContext) -> None:

    async def question_generation(callback_data: str):
        from additional_functions import cache
        data = await cache.get(int(callback_data))
        information = json.loads(data)
        result = ''
        for key, value in information.items():
            await state.update_data(question=value)
            if key == 'lp_user_id':
                continue
            result += f'{key}: {value}\n'

        lp_user_info = await db.get_lp_user_info(lp_user_id=information['lp_user_id'])
        user_name = lp_user_info[0][3] 
        result += f'user_name: {user_name}'
        return information, result

    '''
    Выбор вопроса специалистом
    '''
    if 'question:' in callback.data:
        callback_data = callback.data.split(':')[-1]
        information, result = await question_generation(callback_data=callback_data)
        await state.update_data(question_id=callback_data, user_id=information['lp_user_id'])
        await callback.message.edit_text(result, reply_markup=Specialist_keyboards.question_buttons())
    elif callback.data == 'choose_question':
        markup = InlineKeyboardBuilder()
        data = await state.get_data()
        question_id = data['question_id']
        result_check = db.check_question(question_id=question_id)
        if result_check == 'Вопрос взят':
            await callback.message.edit_text('Выберите другой вопрос', reply_markup=Specialist_keyboards.questions_gen())
        else:
            # await db.answer_process_report(question_id=int(question_id),
            #                          answer='Вопрос взят',
            #                          specialist_id=callback.from_user.id)
            await callback.message.edit_reply_markup(reply_markup=markup.as_markup())
            await callback.message.answer('Введите свой ответ')
            await state.set_state(Specialist_states.answer_question)
    elif callback.data == 'close_question':
        data = await state.get_data()
        await db.answer_process_report(question_id=int(data['question_id']),
                                 answer='Закрытие вопроса',
                                 specialist_id=callback.from_user.id)
        await callback.message.edit_text('Меню', reply_markup=Specialist_keyboards.questions_gen())
    elif callback.data == 'back_to_pool':
        keyboard = await Specialist_keyboards.create_inline_keyboard(callback.from_user.id)
        await callback.message.edit_text('Выберите вопрос', reply_markup=keyboard)
        await state.set_state(Specialist_states.choosing_question)
    elif callback.data == 'dialogue_history':
        data = await state.get_data()
        history_text = "" ; next_string = "\n"
        information_tuple = await db.get_user_history(question_id=int(data['question_id']))
        history = information_tuple[0] ; history = list(history.items())
        user_full_identification = list(information_tuple[1])
        history_text += f'Телеграм-никнейм пользователя: {user_full_identification[1]}{next_string}ФИО пользователя: {user_full_identification[2]}{next_string}{next_string}'
    
        for i in range(len(history)):
            history_text += f"""{''.join([f'{elem[0]} - {elem[1]}{next_string}' for elem in list(history[i][1].items())])}\n\n"""
        await callback.message.edit_text(text=history_text, reply_markup=Specialist_keyboards.question_buttons(condition=int(data['question_id'])))
    elif callback.data == 'answer_the_question':
        keyboard = await Specialist_keyboards.create_inline_keyboard(callback.from_user.id)
        await callback.message.edit_text('Выберите вопрос', reply_markup=keyboard)
        await state.set_state(Specialist_states.choosing_question)


@router.callback_query(User_states.form_choosing)
async def process_starting_general(callback: types.CallbackQuery, state: FSMContext) -> None:
    '''
    Обработка запросов от inline-кнопок форм
    '''
    await state.update_data(tag=callback.data)
    await callback.message.edit_text('Введите Ваш вопрос')
    await state.set_state(User_states.fuzzy_process)

@router.callback_query(Admin_states.registration_process)
async def process_admin(callback: types.CallbackQuery, state: FSMContext) -> None:
    from aiogram import Bot
    from non_script_files.config import API_TELEGRAM
    '''
    Обработка запросов от inline-кнопок admin-a
    '''
    callback_data = callback.data

    if callback_data == 'check_reg':
        await callback.message.edit_text(text="Выберете заявку из предложенных:", reply_markup=Admin_Keyboards.application_gen(await db.get_unregistered()).as_markup())
    elif 'dec_app' in callback_data:
        callback_data = callback_data.split(":")
        await Bot(API_TELEGRAM, parse_mode=ParseMode.HTML).send_message(chat_id = int(callback_data[1]), text="Ваша заявка была отклонена")
        await db.update_registration_status(string_id=callback_data[2],
                                            admin_id=callback.from_user.id,
                                            reg_status="Decline")
        await callback.message.edit_text('Меню', reply_markup=Admin_Keyboards.main_menu())
        await state.set_state(Admin_states.registration_process)
    elif 'acc_app' in callback_data:
        callback_data = callback_data.split(":")
        await Bot(API_TELEGRAM, parse_mode=ParseMode.HTML).send_message(chat_id = int(callback_data[1]), text="Ваша заявка была подтверждена")
        await db.update_registration_status(string_id=callback_data[2],
                                            admin_id=callback.from_user.id,
                                            reg_status="Accept")
        await callback.message.edit_text('Меню', reply_markup=Admin_Keyboards.main_menu())
        await state.set_state(Admin_states.registration_process)
    elif "generated" in callback_data:
        cb_data = callback.data ; cb_data = cb_data.split("&") ; cb_data = cb_data[1].split(":") ; callback_id = int(cb_data[1])
        info_tuple = await db.get_massive_of_values(form_id=callback_id)
        form_info_list, user_info_list = info_tuple[0], info_tuple[1]
        information_panel = f"""Название субъекта: {form_info_list[2]},\nФИО: {form_info_list[3]},\nДолжность: {form_info_list[4]},\nНомер телефона: {form_info_list[5]}"""
        await callback.message.edit_text(text=information_panel, reply_markup=Admin_Keyboards.reg_process_keyboard(form_info_list[1], user_info_list[0]).as_markup())

@router.callback_query()
async def process_user(callback: types.CallbackQuery, state: FSMContext) -> None:
    '''
    Обработка запросов от inline-кнопок user-a
    '''
    @access_block_decorator
    async def getting_started(callback: types.CallbackQuery, state: FSMContext, *args):
        await callback.message.edit_text(text='Добро пожаловать в меню вопросных-форм. Выберете нужную форму', reply_markup=User_Keyboards.section_chose().as_markup())
        await state.set_state(User_states.form_choosing)

    chat_id = callback.from_user.id
    from main import bot
    if callback.data == 'npa':
        await bot.send_document(chat_id=chat_id,
                                document='BQACAgIAAxkBAAIGK2VXPgU1Hi2v-89gziIEgLjchFaQAAJNOAACah64Sl1aSOIk1wABwTME')
        await bot.send_document(chat_id=chat_id,
                                document='BQACAgIAAxkBAAIGLGVXPhfXBvgGqPh1GQJJCgddAxd8AAJPOAACah64SmHR0Xxwyd3YMwQ')
        await bot.send_document(chat_id=chat_id,
                                document='BQACAgIAAxkBAAIGLWVXPmXLgVj-5VDpQsHk47vk2ti3AAJUOAACah64SmgjWufzx-ZPMwQ')
        await bot.send_document(chat_id=chat_id,
                                document='BQACAgIAAxkBAAIGLmVXPy-afxHcCQqjJLwljUV31m9DAAJbOAACah64Sn6s7HayeS3aMwQ')
    elif callback.data == 'main_menu':
        await callback.message.edit_text('Меню', reply_markup=User_Keyboards.main_menu(True).as_markup())
    elif callback.data == 'medstat':
        await bot.send_document(chat_id=chat_id,
                                document='BQACAgIAAxkBAAIGKmVXPf_lixoXHDYS_7vCr9XYg7ZoAAJKOAACah64Sq9HPjDgDOFQMwQ')
    elif callback.data == 'statistic':
        await bot.send_document(chat_id=chat_id,
                                document='BQACAgIAAxkBAAIGJmVXOsMcgevHefPEnQj20Z9ACBUJAAIhOAACah64SvNHf-P94iWtMwQ')
        await bot.send_document(chat_id=chat_id, 
                                document='BQACAgIAAxkBAAIGJ2VXO_9pbBC9S3lWkC_LeDQMxuJPAAI0OAACah64SvOhsb6UYn1GMwQ')
        await bot.send_document(chat_id=chat_id, 
                                document='BQACAgIAAxkBAAIGKGVXPA5hnyS3pN5TKXPzuh7LybSWAAI2OAACah64ShEL9uIIerUSMwQ')
        await bot.send_document(chat_id=chat_id, 
                                document='BQACAgIAAxkBAAIGKWVXPDWvQIvOXfpnGF4eyOAnFpjIAAI5OAACah64SsJyNl0X5tqkMwQ')
    elif callback.data == 'method_recommendations':
        await bot.send_document(chat_id=chat_id, 
                                document='BQACAgIAAxkBAAIGImVXOQABjue_Roq9Eo19YQ0Bigx2AAMYOAACah64SqPPqelSipGuMwQ')
    elif callback.data == 'registration':
        await state.set_state(User_states.reg_fio)
        markup = await User_Keyboards.create_district_buttons()
        await callback.message.edit_text('Выберите Федеральный округ', reply_markup=markup)
    elif callback.data == "make_question":
        await getting_started(callback, state)
    elif callback.data == 'admin_panel':
        await callback.message.edit_text(text="Добро пожаловать в Админ-панель", reply_markup=Admin_Keyboards.main_menu())
        await state.set_state(Admin_states.registration_process)
    elif callback.data == 'specialist_panel':
        await callback.message.edit_text(text="Добро пожаловать в Специалист-панель", reply_markup=Specialist_keyboards.questions_gen())
    elif callback.data == 'user_panel':
        pass
    elif callback.data == 'answer_the_question':
        keyboard = await Specialist_keyboards.create_inline_keyboard(callback.from_user.id)
        await callback.message.edit_text('Выберите вопрос', reply_markup=keyboard)
        await state.set_state(Specialist_states.choosing_question)