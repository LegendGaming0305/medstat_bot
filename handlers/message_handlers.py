from additional_functions import user_registration_decorator, fuzzy_handler, question_redirect, save_to_txt, extracting_query_info, message_delition
from states import User_states, Specialist_states, Admin_states
from main import db
from keyboards import User_Keyboards, Specialist_keyboards, Admin_Keyboards
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
    # elif "Не нашёл подходящего вопроса" in message.text:
    #     await question_redirect(message, state)

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
    await state.update_data(post=message.text)
    await message.answer('''Ваши данные отправлены на проверку, ожидайте подтверждения.
После чего Вы сможете задать вопрос специалисту и получить доступ к каналам разделов форм''', reply_markup=User_Keyboards.main_menu(True).as_markup())
    await db.add_registration_form(message.from_user.id, await state.get_data())
    await db.after_registration_process(message.from_user.id, message.from_user.full_name)
    await state.clear()

@router.message(User_states.fuzzy_process)
async def process_question_input(message: types.Message, state: FSMContext) -> None:
    from cache_container import cache
    '''
    Обработка вопроса через fuzzy_handler
    '''
    await state.update_data(user_question=message.text, user_message=message)
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
        suggestion_menu = await message.answer(text=f"Возможно вы имели в виду:\n{text}", reply_to_message_id=message.message_id, reply_markup=keyboard.as_markup())
        await state.update_data(suggestion_menu=suggestion_menu)
        await message.answer(text=f"""Выберете из представленных выше вопросов наиболее схожий с вашим.\nВ случае, если вы не удовлетворены предложенными вариантами, нажмите 'Не нашёл подходящего вопроса'.""", reply_markup=User_Keyboards.out_of_fuzzy_questions())

@router.message(Specialist_states.answer_question)
async def process_answer(message: types.Message, state: FSMContext) -> None:
    from main import bot
    from cache_container import Data_storage
    data = await state.get_data()
    question_id = data['question_id'] ; question_text = data['question'] ; question_text_for_user = question_text.split("\n")
    form_type = question_text_for_user[1].split(":") ; form_type = form_type[1].strip()
    await db.answer_process_report(question_id=int(question_id),
                             answer=message.text,
                             specialist_id=message.from_user.id)
    form_type = form_type[:25] + "..." if len(form_type) > 25 else form_type
    publication_menu = await bot.send_message(chat_id=message.from_user.id, text="Выберите тип публикации. Для того, чтобы выйти из меню нажмите 'Завершить публикацию'. В противном случае вы не сможете отвечать на другие вопросы", reply_markup=Specialist_keyboards.publication_buttons(spec_forms=form_type))
    await bot.edit_message_text(text=f'<b>Вы выбираете тип публикации для этого вопроса</b>\n{question_text}', chat_id=message.from_user.id, message_id=data['question_message'])
    await state.update_data(menu=publication_menu, spec_answer=message.text)
    await state.set_state(Specialist_states.public_choose_message)
    Data_storage.callback_texts = []

@router.message(Specialist_states.public_choose_file)
async def information_extract(message: types.Message, state: FSMContext) -> None:
    data = await state.get_data()
    query_format_info, file_id = extracting_query_info(query=message)
    spec_forms = await db.get_specform(user_id=message.from_user.id)
    publication_menu = await message.reply(text='Документ успешно загрузился и готов к отправке', reply_markup=Specialist_keyboards.publication_buttons(spec_forms=spec_forms,file_type='other'))
    await state.update_data(menu=publication_menu, query_format_info=query_format_info, file_id=file_id)

@router.message(Admin_states.file_loading)
async def file_reciever(message: types.Message, state: FSMContext):
    from cache_container import cache
    data = await state.get_data()
    
    match data["folder_type"]:
        case 'npa':
            folder_type = "НПА"
        case 'medstat':
            folder_type = "Медстат"
        case 'statistic':
            folder_type = "Статистика"
        case 'method_recommendations':
            folder_type = "Методические рекомендации"

    file_id = message.document.file_id
    file_format = extracting_query_info(message)
    cache_data = await cache.get("file_sending_process")   

    if cache_data:
        cache_data = json.loads(cache_data)
        cache_data.update([(file_id, file_format)])
        serialized_file_info = json.dumps(cache_data)
    else:
        serialized_file_info = json.dumps({file_id:file_format})

    await cache.set(f"file_sending_process", serialized_file_info)
    await message.delete()
    file_one = await message.answer(text=f"Файл {message.document.file_name} успешно загрузился в форму {folder_type}")
    await message_delition(file_one, time_sleep=20)

@router.message(F.document)
async def test(message: types.Message):
    print(message.document)

@router.channel_post(F.text.contains('id'))
async def channelt_id_extraction(post: types.Message):
    print(post)

@router.message(F.text.contains('id'))
async def chat_id_extraction(message: types.Message):
    save_to_txt(chat_information=f'''chat_id={message.chat.id}\nthread_id={message.message_thread_id}''')

@router.message(F.text.contains('8') | F.text.contains('9') | F.text.contains('+7'))
async def sending_information(message: types.Message) -> None:
    '''
    Отправка данных админу из чата координаторов
    '''
    from main import bot
    subject = await db.get_subject_name(user_id=message.from_user.id)
    forward = await bot.send_message(chat_id=5214835464, text=f'Новые полученные данные от пользователя с user_id: {message.from_user.id}\nСубъект: {subject}\n{message.text}')
    await bot.pin_chat_message(chat_id=5214835464, message_id=forward.message_id)
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)

@router.message(F.new_chat_member & F.chat.id == -1002033917658)
async def process_new_member(update: types.ChatMemberUpdated) -> None:
    '''
    Отправка приветственного сообщения при входе пользователя в чат
    '''
    from main import bot
    await bot.send_message(chat_id=-1002033917658,
                           text=f'Добрый день, {update.from_user.full_name}! В целях качественного и оперативного взаимодействия в рамках годового отчета перед началом работы укажите, пожалуйста, Ваши <b>ФИО</b> и <b>номер телефона</b> в сообщении данного чата.\nПример:\n"Иванов Иван Иванович 8 999 999 99-99"',
                           disable_notification=True)