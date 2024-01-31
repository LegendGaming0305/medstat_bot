from additional_functions import user_registration_decorator, fuzzy_handler, question_redirect, save_to_txt, extracting_query_info, message_delition
from additional_functions import delete_member, object_type_generator
from states import User_states, Specialist_states, Admin_states
from main import db
from keyboards import User_Keyboards, Specialist_keyboards
from non_script_files.config import QUESTION_PATTERN, COORD_CHAT

from aiogram.fsm.context import FSMContext
from aiogram import Router, F, types
from aiogram.filters import Command
import json
import datetime
import asyncio
import copy

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
            await state.clear()
        await process_start(message, state)

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
    await db.add_registration_form(message.from_user.id, await state.get_data())
    await db.after_registration_process(message.from_user.id, message.from_user.full_name)
    await db.update_user_info(user_id=message.from_user.id, telegram_name=message.from_user.full_name)
    await message.answer('''Ваши данные отправлены на проверку, ожидайте подтверждения.
После чего Вы сможете задать вопрос специалисту и получить доступ к каналам разделов форм''', reply_markup=await User_Keyboards.main_menu(True, user_id=message.from_user.id))
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
    form_type = question_text_for_user[2].split(":") ; form_type = form_type[1].strip()
    await db.answer_process_report(question_id=int(question_id),
                             answer=message.text,
                             specialist_id=message.from_user.id)
    form_type = form_type[:25] + "..." if len(form_type) > 25 else form_type
    publication_menu = await bot.send_message(chat_id=message.from_user.id, text="Выберите тип публикации. Для того, чтобы выйти из меню нажмите 'Завершить публикацию'. В противном случае вы не сможете отвечать на другие вопросы", reply_markup=Specialist_keyboards.publication_buttons(spec_forms=form_type))
    await bot.edit_message_text(text=f'<b>Вы выбираете тип публикации для этого вопроса</b>\n{question_text}', chat_id=message.from_user.id, message_id=data['question_message'])
    await state.update_data(menu=publication_menu, spec_answer=message.text)
    await state.set_state(Specialist_states.public_choose_message)
    Data_storage.callback_texts = []

@router.message(F.text.contains('/send'))
async def process_sending_ids(message: types.message):
    from main import bot
    info = message.text.split(',')
    user_id = info[0][6:]
    subject = info[1]
    fio = info[2]
    forward = await bot.send_message(chat_id=5214835464, text=f'Новые полученные данные от пользователя с user_id: {user_id}\nСубъект: {subject}\n{fio}')
    await bot.pin_chat_message(chat_id=5214835464, message_id=forward.message_id)

@router.message(Specialist_states.complex_public)
async def information_extract(message: types.Message, state: FSMContext) -> None:
    from cache_container import cache
    data = await state.get_data()
    query_format_info, file_id = extracting_query_info(query=message)
    spec_forms = await db.get_specform(user_id=message.from_user.id)

    if message.document:        
        while spec_forms == None:
            spec_forms = await db.get_specform(user_id=message.from_user.id)

        try:
            if query_format_info["has_caption"] == False and data["not_attached_caption"] != 'Null':
                    query_format_info["caption_text"] = data["not_attached_caption"]
                    query_format_info["has_caption"] = True
                    state.update_data(not_attached_caption='Null')
        except KeyError:
            pass

        try:
            publication_menu = await message.answer(text=f'Документ {query_format_info["file_name"]} успешно загрузился и готов к отправке', reply_markup=Specialist_keyboards.publication_buttons(spec_forms=spec_forms,file_type='other'))
            await cache.set(f"publication_menu:{publication_menu.message_id}", json.dumps([]))
            await state.update_data(data={
                f"publication_menu:{publication_menu.message_id}":publication_menu,
                f"query_format_info:{publication_menu.message_id}":query_format_info,
                f"file_id:{publication_menu.message_id}":file_id})
        except KeyError:
            pass
    else:
        await state.update_data(not_attached_caption=message.text)
        # await asyncio.sleep(3)
        try:
            query_format_info['caption_text'] = message.text
            publication_menu = await message.answer(text=f'Текст сообщения {message.text} успешно загрузился и готов к отправке', reply_markup=Specialist_keyboards.publication_buttons(spec_forms=spec_forms,file_type='other'))
            await cache.set(f"publication_menu:{publication_menu.message_id}", json.dumps([]))
            await state.update_data(data={
                f"publication_menu:{publication_menu.message_id}":publication_menu,
                f"query_format_info:{publication_menu.message_id}":query_format_info,
                f"file_id:{publication_menu.message_id}":file_id})
        except KeyError:
            pass

@router.message(Admin_states.file_loading)
async def file_reciever(message: types.Message, state: FSMContext):  
    from cache_container import Data_storage 
                   
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
            
    file_format = extracting_query_info(message) 
    
    try:
        file_id = message.document.file_id
    except AttributeError:
        pass
    
    try:
        if data["file_sending_process"]:
            pass
    except KeyError:
        await state.update_data(file_sending_process={})
    
    if message.media_group_id == None and file_format[0]["query_format"] != "Text":
        data = await state.get_data()
        data['file_sending_process'].update([(file_id, file_format[0])])
        Data_storage.not_attached_caption = [None, 0]
    elif message.media_group_id == None and file_format[0]["query_format"] == "Text":
        Data_storage.not_attached_caption = [message.text, message.message_id]
        await message.delete()
        return None
    else:
        data = await state.get_data()
        try:
            if data["current_media_group"][0] == message.media_group_id:
                file_format[0]["caption_text"] = data["current_media_group"][1][0] if Data_storage.not_attached_caption[0] != None else "Null"
                file_format[0]["has_caption"] = True if Data_storage.not_attached_caption[0] != None else False
            else:
                try:
                    if Data_storage.not_attached_caption[1] == data["current_media_group"][1][1]:
                        Data_storage.not_attached_caption = [None, 0] 
                    else:
                        pass
                except AttributeError:
                    pass
                if  Data_storage.not_attached_caption[0] != None:
                    file_format[0]["caption_text"] = Data_storage.not_attached_caption[0]
                    file_format[0]["has_caption"] = True
                await state.update_data(current_media_group=(message.media_group_id, Data_storage.not_attached_caption))
        except KeyError:
            if  Data_storage.not_attached_caption[0] != None:
                file_format[0]["caption_text"] = Data_storage.not_attached_caption[0]
                file_format[0]["has_caption"] = True
            await state.update_data(current_media_group=(message.media_group_id, Data_storage.not_attached_caption))
        
        data['file_sending_process'].update([(file_id, file_format[0])])
        
    await message.delete()
    file_one = await message.answer(text=f"Файл {message.document.file_name} успешно загрузился в форму {folder_type}")
    await message_delition(file_one, time_sleep=20)

@router.message(Admin_states.delete_member)
async def get_ids_to_delete(message: types.Message, state: FSMContext):
    from keyboards import Admin_Keyboards
    await state.update_data(ids_to_delete=message.text)
    await message.answer(text='Выберите в каком чате удалить пользователя',
                         reply_markup=Admin_Keyboards.delete_in_chat())

@router.message(F.document)
async def test(message: types.Message):
    print(message.document)

@router.message(F.text.contains('id'))
async def chat_id_extraction(message: types.Message):
    save_to_txt(chat_information=f'''chat_id={message.chat.id}\nthread_id={message.message_thread_id}\nchat_name={message.chat.full_name}\n\n''')

@router.message(F.text.regexp(r'^[\s]*([а-яА-ЯёЁ]+\s[а-яА-ЯёЁ]+\s?[а-яА-ЯёЁ]+)[\s|,]*\+?\d+([\(\s\-]?\d+[\)\s\-]?[\d\s\-]+)?$'))
async def sending_information(message: types.Message) -> None:
    '''
    Отправка данных админу из чата координаторов
    '''
    from main import bot
    from cache_container import cache
    from additional_functions import account_link

    cache_data = await cache.get(f"greeting:{message.from_user.id}")
    subject = await db.get_subject_name(user_id=message.from_user.id)
    try:
        forward = await bot.send_message(chat_id=5214835464, text=f'Новые полученные данные от пользователя с user_id: {message.from_user.id}\nСубъект: {subject}\n{message.text}',
                                         reply_markup=await account_link(message.from_user.url))
        await bot.pin_chat_message(chat_id=5214835464, message_id=forward.message_id)
    except Exception as ex:
        pass
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    await bot.delete_message(chat_id=message.chat.id, message_id=str(cache_data))

@router.message(F.new_chat_member & F.chat.id == COORD_CHAT)
async def process_new_member(update: types.ChatMemberUpdated, state: FSMContext) -> None:
    from cache_container import cache
    from main import bot
    '''
    Отправка приветственного сообщения при входе пользователя в чат
    '''
    from main import bot
    greeting_message = await bot.send_message(chat_id=COORD_CHAT,
                           text=f'Добрый день, {update.from_user.full_name}! В целях качественного и оперативного взаимодействия в рамках годового отчета перед началом работы укажите, пожалуйста, Ваши <b>ФИО</b> и <b>номер телефона</b> в сообщении данного чата.\nПример:\n"Иванов Иван Иванович 8 999 999 99-99"',
                           disable_notification=True)
    serialized_greeting_message = json.dumps(greeting_message.message_id)
    await cache.set(f"greeting:{update.from_user.id}", serialized_greeting_message)

@router.channel_post(F.text.contains('id'))
async def chat_id_extraction(message: types.Message):
    save_to_txt(chat_information=f'''chat_id={message.chat.id}\nthread_id={message.message_thread_id}\nchat_name={message.chat.full_name}\n\n''')