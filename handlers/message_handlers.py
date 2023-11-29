from additional_functions import user_registration_decorator, fuzzy_handler, question_redirect
from states import User_states, Specialist_states
from main import db
from keyboards import User_Keyboards, Specialist_keyboards
from non_script_files.config import QUESTION_PATTERN

from aiogram.fsm.context import FSMContext
from aiogram import Router, F, types
from aiogram.filters import Command
import json

router = Router()

@router.message(Command('start'))
@user_registration_decorator
async def process_start(message: types.Message, state: FSMContext) -> None:
    '''
    Выдаем пользователю определенный набор кнопок от его статуса
    '''
    await state.clear()

@router.message(F.text.contains('Возврат') | F.text.contains('Не нашёл'))
async def exiting_fuzzy(message: types.Message, state: FSMContext):
    await message.delete()
    if "Возврат в главное меню" in message.text:
        @user_registration_decorator
        async def process_start(message: types.Message, state: FSMContext) -> None:
            '''
            Выдаем пользователю определенный набор кнопок от его статуса
            '''
            # await message.reply("Успешный возврат меню...", reply_markup=ReplyKeyboardRemove())
            await state.clear()
        await process_start(message, state)
    elif "Не нашёл подходящего вопроса" in message.text:
        await question_redirect(message, state)

@router.message(User_states.reg_fio)
async def process_fio_input(message: types.Message, state: FSMContext) -> None:
    '''
    Получение ФИО
    '''
    await state.update_data(fio=message.text)
    await message.answer('Введите Вашу должность')
    await state.set_state(User_states.reg_post)

@router.message(User_states.reg_post)
async def process_post_input(message: types.Message, state: FSMContext) -> None:
    '''
    Получение наименования должности
    '''
    await state.update_data(post=message.text)
    await message.answer('Укажите Ваш номер телефона в формате +7 (999) 999-99-99')
    await state.set_state(User_states.reg_telephone_number)

@router.message(User_states.reg_telephone_number)
async def process_telephone_number_input(message: types.Message, state: FSMContext) -> None:
    '''
    Получение номера телефона
    '''
    await state.update_data(telephone_number=message.text)
    await message.answer('''Ваши данные отправлены на проверку, ожидайте подтверждения.
После чего Вы сможете задать вопрос специалисту''', reply_markup=User_Keyboards.main_menu(True).as_markup())
    await db.add_registration_form(message.from_user.id, await state.get_data())
    await db.after_registration_process(message.from_user.id, message.from_user.full_name)
    await state.clear()

@router.message(User_states.fuzzy_process)
async def process_question_input(message: types.Message, state: FSMContext) -> None:
    from cache_container import cache
    '''
    Обработка вопроса через fuzzy_handler
    '''
    await state.update_data(user_question=message.text)
    bot_answer, bot_questions = fuzzy_handler(user_question=message.text, pattern=QUESTION_PATTERN)
    serialized_questions = json.dumps(bot_questions)
    await cache.set(f"questions_pool:{message.from_user.id}", serialized_questions)

    try:
        maximum_simularity = [True for var in bot_questions if var[1][0] >= 85]
    except TypeError:
        maximum_simularity = [False]

    if bot_questions == None:
        await question_redirect(message, state)
    elif True in maximum_simularity:
            await message.reply(text=bot_answer, reply_markup=User_Keyboards.back_to_main_menu().as_markup())
            await state.clear()
    else:
        keyboard, text = User_Keyboards.fuzzy_buttons_generate(bot_questions)
        await message.answer(text=f"Возможно вы имели в виду:\n{text}", reply_to_message_id=message.message_id, reply_markup=keyboard.as_markup())
        await message.answer(text=f"""Выберете из представленных выше вопросов наиболее схожий с вашим.\nВ случае, если вы не удовлетворены предложенными вариантами, нажмите 'Не нашёл подходящего вопроса'.""", reply_markup=User_Keyboards.out_of_fuzzy_questions())

@router.message(Specialist_states.answer_question)
async def process_answer(message: types.Message, state: FSMContext):
    from main import bot
    from cache_container import Data_storage
    await state.update_data(question_answer=message.text)
    data = await state.get_data()
    question_id = data['question_id'] ; question_text = data['question'] ; question_text_for_user = question_text.split("\n")
    form_type = question_text_for_user[1].split(":") ; form_type = form_type[1].strip()
    await db.answer_process_report(question_id=int(question_id),
                             answer=message.text,
                             specialist_id=message.from_user.id)
    await state.set_state(Specialist_states.choosing_publication_destination)
    publication_menu = await bot.send_message(chat_id=message.from_user.id, text="Выберите тип публикации:", reply_markup=Specialist_keyboards.publication_buttons(form_type=form_type))
    await state.update_data(menu=publication_menu)
    Data_storage.callback_texts = []
    
@router.message(F.document)
async def test(message: types.Message):
    print(message.document)