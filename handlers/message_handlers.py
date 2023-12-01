from additional_functions import user_registration_decorator, fuzzy_handler, question_redirect
from states import User_states, Specialist_states
from main import db
from keyboards import User_Keyboards, Specialist_keyboards
from non_script_files.config import QUESTION_PATTERN
import asyncio

from aiogram.fsm.context import FSMContext
from aiogram import Router, F, types
from aiogram.filters import Command
import json
from aiogram.types import ReplyKeyboardRemove

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

@router.message(User_states.reg_organisation)
async def process_fio_input(message: types.Message, state: FSMContext) -> None:
    '''
    Получение места работы
    '''
    await state.update_data(organisation=message.text)
    await message.answer('Введите Вашу должность')
    await state.set_state(User_states.reg_post)

@router.message(User_states.reg_post)
async def process_telephone_number_input(message: types.Message, state: FSMContext) -> None:
    '''
    Получение наименования должности
    '''
    from main import bot
    await state.update_data(post=message.text)
    link = await bot.create_chat_invite_link(chat_id=-1002033917658,
                                          name='Чат координаторов',
                                          member_limit=1)
    await message.answer(f'Пройдите по данной ссылке и заполните дополнительную информацию {link.invite_link}')
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
async def process_answer(message: types.Message, state: FSMContext) -> None:
    from main import bot
    data = await state.get_data()
    question_id = data['question_id']
    answer_message_id = data['question_message']
    question_text = data['question']
    question_text_for_user = question_text.split("\n")
    await db.answer_process_report(question_id=int(question_id),
                             answer=message.text,
                             specialist_id=message.from_user.id)
    await message.reply('Ответ отправлен')
    await state.set_state(Specialist_states.public_choose)
    await bot.edit_message_text(text=f'<b>Вы ответили на этот вопрос</b>\n{question_text}', chat_id=message.from_user.id,
                                message_id=answer_message_id)
    text = await message.answer(text=f'Куда отправить эти данные\n{question_text_for_user[2]}\nОтвет: {message.text}', 
                         reply_markup=Specialist_keyboards.forward_buttons())
    await state.update_data(answer=message.text, text_id=text.message_id)

@router.message(F.document)
async def test(message: types.Message):
    print(message.document)

@router.channel_post(F.text.contains('id'))
async def channelt_id_extraction(post: types.Message):
    print(post)

@router.message(F.text.contains('id'))
async def chat_id_extraction(message: types.Message):
    print(message.chat.id)
    print(message.message_thread_id)

@router.message(F.text.contains('#данные'))
async def sending_information(message: types.Message) -> None:
    '''
    Отправка данных админу из чата координаторов
    '''
    from main import bot
    await bot.send_message(chat_id=5214835464, text=f'Новые полученные данные {message.text}')

@router.message(F.new_chat_member & F.chat.id == -1002033917658)
async def process_new_member(update: types.ChatMemberUpdated) -> None:
    '''
    Отправка приветственного сообщения при входе пользователя в чат
    '''
    from main import bot
    await bot.send_message(chat_id=-1002033917658,
                           text=f'Добрый день, {update.from_user.full_name}! В целях качественного и оперативного взаимодействия в рамках годового отчета перед началом работы укажите, пожалуйста, Ваши <b>ФИО</b> и <b>номер телефона</b> в сообщении данного чата.\nПример:\n"Иванов Иван Иванович 8 999 999 99-99 #данные"')