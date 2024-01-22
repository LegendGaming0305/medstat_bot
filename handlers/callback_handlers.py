from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import FSInputFile
import json
from aiogram.exceptions import TelegramBadRequest
import re
import datetime

from keyboards import Admin_Keyboards, User_Keyboards, Specialist_keyboards
from db_actions import Database
from states import Admin_states, Specialist_states, User_states
from additional_functions import access_block_decorator, create_questions, fuzzy_handler, creating_excel_users, extracting_query_info, message_delition, question_redirect
from additional_functions import document_loading, object_type_generator, save_to_txt
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
        await state.set_state(User_states.reg_organisation)
        await state.update_data(subject=miac_name)
        await callback.message.edit_text('Введите название вашего места работы')

@router.callback_query(User_states.fuzzy_process)
async def catch_questions(callback: types.CallbackQuery, state: FSMContext):
    callback_data = callback.data
    
    try:
        data = await cache.get(f"questions_pool:{callback.from_user.id}")
        information = json.loads(data)
    except TypeError:
        await callback.answer(text="Просим отправить ваш вопрос по указанной вами форме")

    if "fuzzy_buttons" in callback_data:
        callback_data = callback_data.split("&") ; callback_data = callback_data[2] ; callback_data = callback_data.split(":") 
        value_id = int(callback_data[1])
        current_question = list(filter(lambda x: value_id == x[0], information))
        current_question = current_question[0][1][1]
        bot_answer, bot_questions = fuzzy_handler(user_question=current_question, pattern=QUESTION_PATTERN)
        await callback.message.edit_text(text=f"Вопрос: {current_question}\nОтвет: {bot_answer}", reply_markup=User_Keyboards.back_to_fuzzy_questions().as_markup())
    elif callback_data == "back_to_fuzzy":
        keyboard, text = User_Keyboards.fuzzy_buttons_generate(information)
        suggestion_menu = await callback.message.edit_text(text=f"Возможно вы имели в виду:\n{text}", reply_markup=keyboard.as_markup())
        await state.update_data(suggestion_menu=suggestion_menu)
    elif callback_data == "not_found_question":
        data = await state.get_data()
        await data['suggestion_menu'].delete()
        await callback.message.edit_text(inline_message_id=str(data["user_message"].message_id), text=f'Ваш вопрос - {data["user_question"]} - по форме {data["form_info"]["form_name"]} передан')
        await question_redirect(callback, state)
    else:
        await callback.answer(text="Просим отправить ваш вопрос по указанной вами форме")

@router.callback_query(Specialist_states.complex_public)
async def non_message_data(callback: types.CallbackQuery, state: FSMContext) -> None:
    from non_script_files.config import FORMS, RASDEL_FORM
    from cache_container import cache
    from main import bot

    if 'other' in callback.data:
        data = await state.get_data()
        menu_id = callback.message.message_id
        file_dict, file_id = data[f'query_format_info:{menu_id}'], data[f'file_id:{menu_id}']
        menu_cache = await cache.get(f"publication_menu:{data[f'publication_menu:{menu_id}'].message_id}") ; menu_cache = json.loads(menu_cache)
        spec_forms = await db.get_specform(user_id=callback.from_user.id)

        if 'form' in callback.data:
            form_id = int(re.findall(r"\d\d?", callback.data)[0])            

            for key, value in FORMS.items():
                if key in menu_cache: 
                    continue

                if value == form_id:
                    form_type = key
                    break
            
            menu_cache.append(form_type)
            passed_forms = list(filter(lambda x: x["form_name"] not in menu_cache, spec_forms))
            found_patterns = ("open", ) if "open" in menu_cache else ()
            await cache.set(f"publication_menu:{data[f'publication_menu:{menu_id}'].message_id}", json.dumps(menu_cache))

            match file_dict['query_format']:
                case 'Document': await bot.send_document(chat_id=RASDEL_FORM, 
                                                         document=file_id, message_thread_id=FORMS[form_type], 
                                                         caption=file_dict['caption_text'])
                case 'Photo': pass
                case 'Video': pass
                case 'Text': await bot.send_message(chat_id=RASDEL_FORM,
                                                    message_thread_id=FORMS[form_type],
                                                    text=data["not_attached_caption"])

            await callback.message.edit_reply_markup(inline_message_id=str(data[f'publication_menu:{menu_id}'].message_id), reply_markup=Specialist_keyboards.publication_buttons(file_type='other', passed_forms_info=passed_forms, found_patterns=found_patterns))
            message = await callback.message.reply(f'Информация отправлена в канал формы: {form_type}')
            await message_delition(message, time_sleep=10)
            await db.add_suggestion_to_post(post_content=file_id, post_suggestor=callback.from_user.id, pub_type_tuple=tuple(file_dict.values()), pub_state='Accept')
        elif 'open_chat' in callback.data:
            menu_cache.append("open") ; await cache.set(f"publication_menu:{data[f'publication_menu:{menu_id}'].message_id}", json.dumps(menu_cache))
            passed_forms = list(filter(lambda x: x["form_name"] not in menu_cache, spec_forms))
            await callback.message.edit_reply_markup(inline_message_id=str(data[f'publication_menu:{menu_id}'].message_id), reply_markup=Specialist_keyboards.publication_buttons(file_type='other', passed_forms_info=passed_forms, found_patterns=('open', )))
            message = await callback.message.answer('Запрос на публикацию в открытом канале отправлен')
            await message_delition(message, time_sleep=10)
            await db.add_suggestion_to_post(post_content=file_id, post_suggestor=callback.from_user.id, pub_type_tuple=tuple(file_dict.values()))

    if callback.data == 'finish_state':
        await callback.answer(text='Вы успешно завершили процесс')
        await callback.message.delete()
        message = await callback.message.answer('Теперь вы можете вернуться в главное меню или опубликовать другой файл')
        await message_delition(message, time_sleep=10)
        # await state.set_state(Specialist_states.choosing_question)

@router.callback_query(Specialist_states.public_choose_message)
async def redirecting_data(callback: types.CallbackQuery, state: FSMContext) -> None:
    '''Обработка текстовых сообщений - вопрос-ответов'''
    from main import bot
    from cache_container import Data_storage
    from keyboards import BUTTONS_TO_NUMBER
    from non_script_files.config import FORMS, RASDEL_FORM

    await state.set_state(Specialist_states.choosing_question)
    data = await state.get_data()
    
    def callback_addition():
        nonlocal BUTTONS_TO_NUMBER, Data_storage
        found_data = []
        for row in Data_storage.callback_texts:
            for pattern in BUTTONS_TO_NUMBER.keys():
                if pattern in row:
                    found_data.append(pattern)
        return set(found_data)

    question_message_id = await db.get_question_message_id(question_id=data['question_id'])
    question_text = data['question'] ; question_text_for_user = question_text.split("\n")
    question = question_text.split(':</b>')[1].split(':\n<s>')[0].strip()
    tuple_of_info = await db.get_lp_user_info(lp_user_id=data['user_id'])
    user_id = tuple_of_info[1][1]
    form_type = question_text_for_user[2].split(":") ; form_type = form_type[1].strip()
    form_type = form_type[:25] + "..." if len(form_type) > 25 else form_type

    try:
        await bot.edit_message_text(text=f'<b>Вы выбираете тип публикации для этого вопроса</b>\n{question_text}', chat_id=callback.from_user.id, message_id=data['question_message'])
    except TelegramBadRequest:
        pass
    await state.set_state(Specialist_states.public_choose_message)

    Data_storage.callback_texts.append(callback.data)
    
    if callback.data == "private_message":
        found_data = tuple(callback_addition())
        await callback.message.edit_reply_markup(inline_message_id=str(data['menu'].message_id), reply_markup=Specialist_keyboards.publication_buttons(spec_forms=form_type, found_patterns=found_data))
        await bot.send_message(chat_id=user_id, text=f'{question}\n<b>Ответ</b>: {data["spec_answer"]}', reply_to_message_id=question_message_id)
        message = await callback.message.reply(f'Ответ отправлен пользователю в личные сообщения')
        await message_delition(message, time_sleep=10)
    elif "form_type" in callback.data:
        found_data = tuple(callback_addition())
        await callback.message.edit_reply_markup(inline_message_id=str(data['menu'].message_id), reply_markup=Specialist_keyboards.publication_buttons(spec_forms=form_type, found_patterns=found_data))
        await bot.send_message(chat_id=-1001994572201, text=f'{question}\n<b>Ответ</b>: {data["spec_answer"]}', message_thread_id=FORMS[form_type])
        query_dict, file_id = extracting_query_info(query=callback)
        await db.add_suggestion_to_post(post_content=f'{question_text_for_user[3]}\n<b>Ответ</b>: {data["spec_answer"]}', post_suggestor=callback.from_user.id, pub_type_tuple=tuple(query_dict.values()), pub_state='Accept')
        message = await callback.message.reply(f'Ответ отправлен в канал формы: {form_type}')
        await message_delition(message, time_sleep=10)
    elif callback.data == 'open_chat_public':
        found_data = tuple(callback_addition())
        await callback.message.edit_reply_markup(inline_message_id=str(data['menu'].message_id), reply_markup=Specialist_keyboards.publication_buttons(spec_forms=form_type, found_patterns=found_data))
        query_dict, file_id = extracting_query_info(query=callback)
        query_dict['query_format'] = 'Answer'
        await db.add_suggestion_to_post(post_content=f'{question}\n<b>Ответ</b>: {data["spec_answer"]}', post_suggestor=callback.from_user.id, pub_type_tuple=tuple(query_dict.values()))
        message = await callback.message.answer('Запрос на публикацию в открытом канале отправлен')
        await message_delition(message, time_sleep=10)
    elif callback.data == 'finish_state':
        await bot.edit_message_text(text=f'<b>Вы успешно ответили на этот вопрос</b>\n{question_text}', chat_id=callback.from_user.id, message_id=data['question_message'])
        await callback.answer(text='Вы успешно завершили процесс')
        await callback.message.delete()
        message = await callback.message.answer('Теперь вы можете выбирать другие вопросы для ответа')
        await state.set_state(Specialist_states.choosing_question)
        await message_delition(message, time_sleep=10)
        
@router.callback_query(Specialist_states.choosing_question)
async def process_answers(callback: types.CallbackQuery, state: FSMContext) -> None:
    '''
    Выбор вопроса специалистом
    '''
    if 'dialogue_history' in callback.data:
        from cache_container import Data_storage
        page_number = 1
        history_text = "" ; NEXT_STRING = "\n"

        if "limit" in callback.data or "offset" in callback.data:
            passed_values = callback.data.split("&") ; passed_values = passed_values[1].split(":") ; passed_values = int(passed_values[1])
            page_number = 1 if passed_values == 4 else passed_values // 4 
            information_tuple = await db.get_user_history(question_id=Data_storage.question_id, values_range=[4, 4 * page_number])
        else:
            id = callback.message.html_text.split('<s>')[1].strip()
            message_id = int(id[:len(id) - 4])
            question_info = callback.message.html_text.split('</b>')
            Data_storage.question_id = await db.get_question_id(question=question_info[1].split(':')[0].strip(),
                                                                message_id=message_id)
            information_tuple = await db.get_user_history(question_id=Data_storage.question_id)

        history = information_tuple[0] ; history = list(history.items())
        user_full_identification = list(information_tuple[1])
    
        for i in range(len(history)):
            history_text += f"""{''.join([f'{elem[0]} - {elem[1]}{NEXT_STRING}' for elem in list(history[i][1].items())])}\n\n"""
        history_text += f"Номер страницы: {page_number + 1}"
        await callback.message.edit_text(text=history_text, reply_markup=Specialist_keyboards.question_buttons(condition=(Data_storage.question_id, information_tuple[2], 4 * page_number)))
    elif callback.data == 'answer_the_question':
        await state.set_state(Specialist_states.choosing_question)
        questions = await create_questions(callback.from_user.id)
        await callback.message.edit_text('Выберите вопрос')
        message_ids = []
        for question in questions:
            lp_user_info = await db.get_lp_user_info(lp_user_id=question['lp_user_id'])
            user_name = lp_user_info[0][1]
            message = await callback.message.answer(f'Пользователь: {user_name}\nСубъект: {question["subject_name"]}\nФорма: {question["form_name"]}\n<b>Вопрос:</b> {question["question"]}:\n<s>{question["message_id"]}</s>', 
                                                    reply_markup=Specialist_keyboards.question_buttons())
            message_ids.append(message.message_id)
        await callback.message.answer('Если вопросы закончились (нет больше кнопок у них), то нажмите здесь кнопку для генерации новых',
                                    reply_markup=Specialist_keyboards.questions_gen())
        try:
            await state.update_data(message_ids=message_ids)
        except UnboundLocalError:
            pass
    elif callback.data == 'choose_question':
        markup = InlineKeyboardBuilder()
        id = callback.message.html_text.split('<s>')[1].strip()
        message_id = int(id[:len(id) - 4])
        question_info = callback.message.html_text.split('</b>')
        question_id = await db.get_question_id(question=callback.message.text.split('Вопрос:')[1].split(':\n')[0].strip(),
                                               message_id=message_id)
        result_check = await db.check_question(question_id=question_id, message_id=message_id)
        lp_user_id = await db.get_user_id(question=callback.message.text.split(':')[4].strip(), message_id=message_id)
        if result_check == 'Вопрос взят':
            await callback.message.edit_text(f'<b>Вопрос взят</b>\n{callback.message.html_text}')
            await callback.message.answer('Выберите другой вопрос, так как на этот уже отвечает другой специалист')
        else:
            await db.answer_process_report(question_id=int(question_id),
                                     answer='Вопрос взят',
                                     specialist_id=callback.from_user.id)
            await callback.message.edit_reply_markup(reply_markup=markup.as_markup())
            edit = await callback.message.edit_text(f'<b>Выбранный вопрос</b>\n{callback.message.html_text}')
            await callback.message.answer('Введите свой ответ')
            await state.set_state(Specialist_states.answer_question)
            await state.update_data(question_id=question_id, question_message=edit.message_id,
                                    question=callback.message.html_text,
                                    user_id=lp_user_id)
    elif callback.data == 'close_question':
        id = callback.message.html_text.split('<s>')[1].strip()
        message_id = int(id[:len(id) - 4])
        question_info = callback.message.html_text.split('</b>')
        question_id = await db.get_question_id(question=question_info[1].split(':')[0].strip(),
                                               message_id=message_id)
        await db.answer_process_report(question_id=int(question_id),
                                 answer='Закрытие вопроса',
                                 specialist_id=callback.from_user.id)
        await callback.message.edit_text(f'<b>Вопрос закрыт</b>\n{callback.message.html_text}')
    elif 'back_to_question' in callback.data:
        questions = await create_questions(callback.from_user.id)
        question_id = callback.data ; question_id = question_id.split(":") ; question_id = int(question_id[1])
        question_info = await db.get_question_id(inputed_question_id=question_id)

        data = {'question': question_info['question_content'],
                'lp_user_id': question_info['lp_user_id'],
                'form_name': question_info['form_name'],
                'message_id': question_info['question_message']}
        
        lp_user_info = await db.get_lp_user_info(lp_user_id=data['lp_user_id']) ; user_name = lp_user_info[0][3]
        message = await callback.message.edit_text(text=f'Пользователь: {user_name}\nФорма: {data["form_name"]}\n<b>Вопрос:</b> {data["question"]}:\n<s>{data["message_id"]}</s>', 
                                        reply_markup=Specialist_keyboards.question_buttons())

@router.callback_query(Admin_states.delete_member)
async def delete_chat_members(callback: types.CallbackQuery, state: FSMContext) -> None:
    '''
    Удаление пользователя из чата
    '''
    data = await state.get_data()
    ids = data['ids_to_delete']
    from non_script_files.config import COORD_CHAT
    from additional_functions import delete_member
    if callback.data == 'coord_chat':
        await delete_member(message=ids, chat_id=COORD_CHAT)
    await state.clear()
    await callback.message.answer('Пользователь удален из чата', 
                                  reply_markup=Admin_Keyboards.main_menu())

@router.callback_query(User_states.form_choosing)
async def process_starting_general(callback: types.CallbackQuery, state: FSMContext) -> None:
    from non_script_files.config import COORD_CHAT
    '''
    Обработка запросов от inline-кнопок форм
    '''
    from main import bot
    from non_script_files.config import COORD_CHAT
    if callback.data == 'sec_ten':
        link = await bot.create_chat_invite_link(chat_id=COORD_CHAT,
                                          name='Чат координаторов',
                                          member_limit=1)
        await callback.message.answer(text=f'Ссылка на чат координаторов {link.invite_link}')
        await callback.message.edit_text(text='Меню', reply_markup=User_Keyboards.main_menu(True).as_markup())
        await state.clear()
    elif callback.data == 'main_menu':
        await callback.message.edit_text('Меню', reply_markup=User_Keyboards.main_menu(True).as_markup())
        await state.clear()
    else:
        await state.update_data(tag=callback.data)
        form_info = await db.extract_form_info_by_tag(tag_info=callback.data)
        await state.update_data(form_info=form_info)
        data = await state.get_data()
        form_name_for_alert = form_info["form_name"][:40] + "..." if len(form_info["form_name"]) > 40 else form_info["form_name"]
        await callback.answer(text=f'Вы выбрали форму для отправки - {form_name_for_alert}. Теперь, введите Ваш вопрос', show_alert=True)
        
        try:
            if data["notific_message"]:
                await message_delition(data["notific_message"], time_sleep=0)
            else:
                pass
        except KeyError:
            pass
        
        try:
            await callback.message.edit_text(inline_message_id=str(data["menu"].message_id), text=f"Вы выбрали форму для отправки - {form_info['form_name']}. Для возврата в меню, воспользуйтесь кнопкой 'Возврат в главное меню'", reply_markup=User_Keyboards.section_chose().as_markup())
        except TelegramBadRequest:
            pass

        await state.set_state(User_states.fuzzy_process)
        
@router.callback_query(Admin_states.registration_process)
async def process_admin(callback: types.CallbackQuery, state: FSMContext) -> None:
    page_value = 1
    '''
    Обработка запросов от inline-кнопок admin-a
    '''
    callback_data = callback.data
    from main import bot
    from non_script_files.config import COORD_CHAT
    if 'dec_app' in callback_data:
        callback_data = callback_data.split(":")
        await bot.send_message(chat_id = int(callback_data[1]), text="Ваша заявка была отклонена")
        await db.update_registration_status(string_id=callback_data[2],
                                            admin_id=callback.from_user.id,
                                            reg_status="Decline")
        data = await state.get_data()
        page = int(data['page'])
        await callback.answer(text="Вы отклонили заявку")
        await callback.message.edit_text(text="Выберете заявку из предложенных. Если нету кнопок, прикрепленных к данному сообщению, то заявки не сформировались - вернитесь к данному меню позже", 
                                         reply_markup=Admin_Keyboards.application_gen(page_value=page, unreg_tuple=await db.get_unregistered(passed_values=10*(page - 1), available_values=10)).as_markup())             
    elif 'acc_app' in callback_data:
        callback_data = callback_data.split(":")
        link = await bot.create_chat_invite_link(chat_id=COORD_CHAT,
                                          name='Чат координаторов',
                                          member_limit=1)
        await bot.send_message(chat_id=int(callback_data[1]),
                               text=f'Ваша заявка была подтверждена\nПройдите по данной ссылке и заполните дополнительную информацию {link.invite_link}')
        await db.update_registration_status(string_id=callback_data[2],
                                            admin_id=callback.from_user.id,
                                            reg_status="Accept")
        data = await state.get_data()
        page = int(data['page'])
        await callback.answer(text="Вы приняли заявку")
        await callback.message.edit_text(text="Выберете заявку из предложенных. Если нету кнопок, прикрепленных к данному сообщению, то заявки не сформировались - вернитесь к данному меню позже", 
                                         reply_markup=Admin_Keyboards.application_gen(page_value=page, unreg_tuple=await db.get_unregistered(passed_values=10*(page - 1), available_values=10)).as_markup())             
    elif "generated" in callback_data:
        cb_data = callback.data ; cb_data = cb_data.split("&") ; cb_data = cb_data[1].split(":") ; callback_id = int(cb_data[1])
        info_tuple = await db.get_massive_of_values(form_id=callback_id)
        form_info_list, user_info_list = info_tuple[0], info_tuple[1]
        information_panel = f"""Название субъекта: {form_info_list[2]},\nДолжность: {form_info_list[3]},\nМесто работы(организация): {form_info_list[4]},\nДата регистрации: {form_info_list[5]}"""
        await callback.message.edit_text(text=information_panel, reply_markup=Admin_Keyboards.reg_process_keyboard(form_info_list[1], user_info_list[0]).as_markup())
    elif callback_data == 'check_reg':
        await callback.message.edit_text(text="Выберете заявку из предложенных. Если нету кнопок, прикрепленных к данному сообщению, то заявки не сформировались - вернитесь к данному меню позже", 
                                         reply_markup=Admin_Keyboards.application_gen(page_value=page_value, unreg_tuple=await db.get_unregistered()).as_markup())
        await state.update_data(page='1')
    elif "next_page" in callback_data or "prev_page" in callback_data:
        page_value = callback_data.split(":") ; page_value = int(page_value[1])
        await callback.message.edit_text(text="Выберете заявку из предложенных. Если нету кнопок, прикрепленных к данному сообщению, то заявки не сформировались - вернитесь к данному меню позже", 
                                         reply_markup=Admin_Keyboards.application_gen(page_value=page_value, unreg_tuple=await db.get_unregistered(passed_values=10*(page_value - 1), available_values=10)).as_markup())
        await state.update_data(page=page_value)

@router.callback_query(User_states.file_date)
async def process_getting_files(callback: types.CallbackQuery, state: FSMContext):
    from main import bot
    from keyboards import general_kb
    data = await state.get_data()
    button_type = data['button_type']
    chat_id = callback.from_user.id
    file_info = await db.loading_files(button_type=button_type, time=callback.data)
    for row in file_info:
        if row["file_format"]["caption_text"] == "Null":
            await bot.send_document(chat_id=chat_id, document=row["file_id"])
        else:
            await bot.send_document(chat_id=chat_id, caption=row["file_format"]["caption_text"], document=row["file_id"])

    await state.clear()
    await callback.message.answer(text='Вернитесь в главное меню по кнопке внизу вашего экрана', 
                                  reply_markup=general_kb)

@router.callback_query(Admin_states.post_publication)
async def process_open_chat_publication(callback: types.CallbackQuery, state: FSMContext) -> None:
    '''
    Обработка публикации в открытом канале
    '''
    from main import bot
    from non_script_files.config import OPEN_CHANNEL
    if 'accept_post' in callback.data:
        pub_type = callback.data.split("&") ; pub_type = pub_type[1].split(":") ; pub_type = pub_type[1]
        pub_id = callback.data.split("&") ; pub_id = pub_id[2].split(":") ; pub_id = pub_id[1]
        
        match pub_type.capitalize():
            case 'Text': 
                await bot.send_message(chat_id=OPEN_CHANNEL, text=callback.message.html_text)
                await callback.message.edit_text(text=f'<b>Вы одобрили публикацию этого поста</b>\n{callback.message.html_text}')
            case 'Document': 
                await bot.send_document(chat_id=OPEN_CHANNEL, document=callback.message.document.file_id, caption=callback.message.html_text)
                await callback.message.edit_caption(caption=f'<b>Вы одобрили публикацию этого поста</b>\n{callback.message.html_text}')

        await db.update_publication_status(pub_id=int(pub_id),
                                           publication_status='Accept')
    elif 'decline_post' in callback.data:
        pub_type = callback.data.split("&") ; pub_type = pub_type[1].split(":") ; pub_type = pub_type[1]
        pub_id = callback.data.split("&") ; pub_id = pub_id[2].split(":") ; pub_id = pub_id[1]
        
        match pub_type.capitalize():
            case 'Text': 
                await callback.message.edit_text(text=f'<b>Вы отклонили этот пост</b>\n{callback.message.html_text}')
            case 'Document': 
                await callback.message.edit_caption(caption=f'<b>Вы отклонили этот пост</b>\n{callback.message.html_text}')

        await db.update_publication_status(pub_id=int(pub_id), 
                                           publication_status='Decline')
    elif callback.data == 'publications':
        publications = await db.get_posts_to_public()
        for publication in publications:
            if publication['publication_type']['publication_format'] == 'Text':
                await callback.message.answer(text=publication['publication_type']['caption_text'], reply_markup=Admin_Keyboards.post_publication(post_id=publication['id']))
            elif publication['publication_type']['publication_format'] == 'Answer':
                await callback.message.answer(text=publication['publication_content'], reply_markup=Admin_Keyboards.post_publication(post_id=publication['id']))
            elif publication['publication_type']['publication_format'] == 'Document': 
                await bot.send_document(chat_id=callback.from_user.id, caption=publication['publication_type']['caption_text'], document=publication['publication_content'], reply_markup=Admin_Keyboards.post_publication(pub_type='document', post_id=publication['id']))
        await callback.message.answer(text='Если публикации закончились (нет больше кнопок у них), то нажмите здесь кнопку для генерации новых', reply_markup=Admin_Keyboards.pub_refresh())
        await state.set_state(Admin_states.post_publication)
        
@router.callback_query(Admin_states.file_loading)
async def upload_file(callback: types.CallbackQuery, state: FSMContext) -> None:
    from cache_container import Data_storage
    from main import bot
    if callback.data == "npa":
        await state.update_data(folder_type="npa")
        data = await state.get_data()
        await callback.message.edit_text(inline_message_id=str(data['inline_menu'].message_id), text="Прикрепите файл(ы) и при необходимости добавьте описание. Для завершения процесса отправки нажмите на кнопку 'Завершить загрузку'. В противном случае загруженные вами файлы НЕ загрузятся в систему. Для отмены действия вернитесь в главное меню, нажав на соответствующую кнопку.", reply_markup=Admin_Keyboards.file_loading(True))
    elif callback.data == "medstat":
        await state.update_data(folder_type="medstat")
        data = await state.get_data()
        await callback.message.edit_text(inline_message_id=str(data['inline_menu'].message_id), text="Прикрепите файл(ы) и при необходимости добавьте описание. Для завершения процесса отправки нажмите на кнопку 'Завершить загрузку'. В противном случае загруженные вами файлы НЕ загрузятся в систему. Для отмены действия вернитесь в главное меню, нажав на соответствующую кнопку.", reply_markup=Admin_Keyboards.file_loading(True))
    elif callback.data == "statistic":
        await state.update_data(folder_type="statistic")
        data = await state.get_data()
        await callback.message.edit_text(inline_message_id=str(data['inline_menu'].message_id), text="Прикрепите файл(ы) и при необходимости добавьте описание. Для завершения процесса отправки нажмите на кнопку 'Завершить загрузку'. В противном случае загруженные вами файлы НЕ загрузятся в систему. Для отмены действия вернитесь в главное меню, нажав на соответствующую кнопку.", reply_markup=Admin_Keyboards.file_loading(True))
    elif callback.data == "method_recommendations":
        await state.update_data(folder_type="method_recommendations")
        data = await state.get_data()
        await callback.message.edit_text(inline_message_id=str(data['inline_menu'].message_id), text="Прикрепите файл(ы) и при необходимости добавьте описание. Для завершения процесса отправки нажмите на кнопку 'Завершить загрузку'. В противном случае загруженные вами файлы НЕ загрузятся в систему. Для отмены действия вернитесь в главное меню, нажав на соответствующую кнопку.", reply_markup=Admin_Keyboards.file_loading(True))
    elif callback.data == "check_loaded":
        data = await state.get_data()
        try:
            files = data["file_sending_process"]
        except KeyError:
            await callback.answer(text="Вы ещё не загрузили файлы")
            return None
        loaded_text = "Ниже представлены файлы и подписи к ним, которые вы загрузили в текущей сессии.\n\n"
        
        for dict_instance in files.values(): 
            string = f'{dict_instance["file_name"]}: {dict_instance["caption_text"]}\n'
            loaded_text += "------------------------------------------------------------------------------------------\n" + string + "------------------------------------------------------------------------------------------\n\n"
        
        txt_report = save_to_txt(loaded_files=f"{datetime.datetime.now()}\n\n{loaded_text}", save_mode="w+")
        txt_report = FSInputFile('loaded_files.txt')
        
        try:
            await callback.message.edit_text(text=loaded_text, reply_markup=Admin_Keyboards.file_loading(True))
        except TelegramBadRequest: 
            try:
                await callback.message.edit_text(text=loaded_text[:4096], reply_markup=Admin_Keyboards.file_loading(True))
            except TelegramBadRequest:
                pass
            await bot.send_document(chat_id=Data_storage.user_id, document=txt_report, caption="В случае, если телеграм обрезает сообщение, высылается файл со всей информацией текущей сессии")
        
    elif callback.data == "cancel_loading":
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
        
        files = data["file_sending_process"]
        await document_loading(button_name=data['folder_type'], doc_info=files)

        menu = await callback.message.edit_text(inline_message_id=str(data['inline_menu'].message_id), text="Процесс загрузки в форму успешно завершен. Выберете в какой раздел загружать файлы", reply_markup=Admin_Keyboards.file_loading())
        await state.update_data(inline_menu=menu)

@router.callback_query(Admin_states.answers_form)
async def process_choosing_answers_form(callback: types.CallbackQuery, state: FSMContext):
    '''
    Обработка и выдача вопрос по определенной форме для админов
    '''
    from additional_functions import create_questions
    await state.set_state(Specialist_states.choosing_question)
    questions = await create_questions(specialist_id=callback.from_user.id, form=callback.data)
    await callback.message.edit_text('Выберите вопрос')
    message_ids = []
    for question in questions:
        lp_user_info = await db.get_lp_user_info(lp_user_id=question['lp_user_id'])
        user_name = lp_user_info[0][1]
        message = await callback.message.answer(f'Пользователь: {user_name}\nСубъект: {question["subject_name"]}\nФорма: {question["form_name"]}\n<b>Вопрос:</b> {question["question"]}:\n<s>{question["message_id"]}</s>', 
                                                reply_markup=Specialist_keyboards.question_buttons())
        message_ids.append(message.message_id)
    await callback.message.answer('Если вопросы закончились (нет больше кнопок у них), то нажмите здесь кнопку для генерации новых',
                                reply_markup=Specialist_keyboards.questions_gen())
    try:
        await state.update_data(message_ids=message_ids)
    except UnboundLocalError:
        pass

@router.callback_query()
async def process_user(callback: types.CallbackQuery, state: FSMContext) -> None:
    '''
    Обработка запросов от inline-кнопок user-a
    '''

    @access_block_decorator
    async def getting_started(callback: types.CallbackQuery, state: FSMContext):
        await state.set_state(User_states.form_choosing)
        menu_info = await callback.message.edit_text(text='Добро пожаловать в меню вопросных-форм. Выберете нужную форму. Для возврата в меню, воспользуйтесь кнопкой "Возврат в главное меню"', reply_markup=User_Keyboards.section_chose().as_markup())
        await state.update_data(menu=menu_info)
        
    @access_block_decorator
    async def getting_link(callback: types.CallbackQuery, state: FSMContext):
        await callback.message.answer('Ссылка на канал раздела форм - https://t.me/+cNQvBD_FWpQxZWRi')

    chat_id = callback.from_user.id
    from main import bot

    if callback.data == 'main_menu':
        await callback.message.edit_text('Меню', reply_markup=User_Keyboards.main_menu(True).as_markup())
    elif callback.data == 'npa':
        await state.set_state(User_states.file_date)
        await state.update_data(button_type='npa')
        await callback.message.edit_text(text='Выберите период времени', reply_markup=User_Keyboards.show_files())
    elif callback.data == 'medstat':
        await state.set_state(User_states.file_date)
        await state.update_data(button_type='medstat')
        await callback.message.edit_text(text='Выберите период времени', reply_markup=User_Keyboards.show_files())
    elif callback.data == 'statistic':
        await state.set_state(User_states.file_date)
        await state.update_data(button_type='statistic')
        await callback.message.edit_text(text='Выберите период времени', reply_markup=User_Keyboards.show_files())
    elif callback.data == 'method_recommendations':
        await state.set_state(User_states.file_date)
        await state.update_data(button_type='method_recommendations')
        await callback.message.edit_text(text='Выберите период времени', reply_markup=User_Keyboards.show_files())
    elif callback.data == 'registration':
        await state.set_state(User_states.reg_organisation)
        markup = await User_Keyboards.create_district_buttons()
        await callback.message.edit_text('Выберите Федеральный округ', reply_markup=markup)
    elif callback.data == "make_question":
        await getting_started(callback, state)
    elif callback.data == 'admin_panel':
        await state.clear()
        menu = await callback.message.edit_text(text="Добро пожаловать в Админ-панель", reply_markup=Admin_Keyboards.main_menu())
        await state.update_data(main_menu=menu)
    elif callback.data == 'specialist_panel':
        await callback.message.edit_text(text="Добро пожаловать в Специалист-панель", reply_markup=Specialist_keyboards.main_menu())
    elif callback.data == 'link_open_chat':
        await callback.answer('Вы перешли в открытый канал')
    elif callback.data == 'link_razdel_chat':
        await getting_link(callback, state)
    elif callback.data == 'chats_and_channels':
        await callback.message.edit_text(text="Выберете чат\канал в который хотите перейти", reply_markup=Admin_Keyboards.access_to_channels())
    elif callback.data == 'complex_upload':
        await callback.message.edit_text(text='Прикрепите файл и текстовое описание к нему или же вы можете написать текстовое сообщение-объявление для отправки в раздел форм')
        await state.set_state(Specialist_states.complex_public)
    elif callback.data == 'answer_the_question':
        from additional_functions import choose_form
        result = await choose_form(user_id=callback.from_user.id, callback=callback)
        if result is True:
            await state.set_state(Admin_states.answers_form)
            return
        await state.set_state(Specialist_states.choosing_question)
        questions = await create_questions(callback.from_user.id)
        await callback.message.edit_text('Выберите вопрос')
        message_ids = []
        for question in questions:
            lp_user_info = await db.get_lp_user_info(lp_user_id=question['lp_user_id'])
            user_name = lp_user_info[0][1]
            message = await callback.message.answer(f'Пользователь: {user_name}\nСубъект: {question["subject_name"]}\nФорма: {question["form_name"]}\n<b>Вопрос:</b> {question["question"]}:\n<s>{question["message_id"]}</s>', 
                                                    reply_markup=Specialist_keyboards.question_buttons())
            message_ids.append(message.message_id)
        await callback.message.answer('Если вопросы закончились (нет больше кнопок у них), то нажмите здесь кнопку для генерации новых',
                                    reply_markup=Specialist_keyboards.questions_gen())
        try:
            await state.update_data(message_ids=message_ids)
        except UnboundLocalError:
            pass
    elif callback.data == 'check_reg':
        await callback.message.edit_text(text="""Выберете заявку из предложенных. Если нету кнопок, прикрепленных к данному сообщению, то заявки не сформировались - вернитесь к данному меню позже. Для возврата в главное меню воспользуйтесь кнопкой 'Возврат в главное меню'""", reply_markup=Admin_Keyboards.application_gen(page_value=1, unreg_tuple=await db.get_unregistered()).as_markup())
        await state.set_state(Admin_states.registration_process)
        await state.update_data(page='1')
        await state.update_data(page='1')
    elif callback.data == 'publications':
        publications = await db.get_posts_to_public()
        data = await state.get_data()
        for publication in publications:
            if publication['publication_type']['publication_format'] == 'Text':
                await callback.message.answer(text=publication['publication_type']['caption_text'], reply_markup=Admin_Keyboards.post_publication(post_id=publication['id']))
            elif publication['publication_type']['publication_format'] == 'Answer':
                await callback.message.answer(text=publication['publication_content'], reply_markup=Admin_Keyboards.post_publication(post_id=publication['id']))
            elif publication['publication_type']['publication_format'] == 'Document': 
                await bot.send_document(chat_id=callback.from_user.id, caption=publication['publication_type']['caption_text'], document=publication['publication_content'], reply_markup=Admin_Keyboards.post_publication(pub_type='document', post_id=publication['id']))
        await callback.message.edit_text(inline_message_id=str(data["main_menu"].message_id), text='Если публикации закончились (нет больше кнопок у них), то нажмите здесь кнопку для генерации новых', reply_markup=Admin_Keyboards.pub_refresh())
        await state.set_state(Admin_states.post_publication)
    elif callback.data == 'op_channel_join':
        await callback.answer(text="Вы перешли в открытый канал")
    elif callback.data == 'coord_chat_join':
        await callback.answer(text='Вы перешли в чат координаторов')
    elif callback.data == 'sections_join':
        await callback.answer(text='Вы перешли в разделы форм')
    elif callback.data == 'registration_db':
        from main import bot
        await creating_excel_users()
        excel = FSInputFile('miac_output.xlsx')
        await bot.send_document(chat_id=callback.from_user.id,
                                document=excel)
    elif callback.data == 'load_file':
        data = await state.get_data()
        await state.set_state(Admin_states.file_loading)
        try:
            menu = await callback.message.edit_text(inline_message_id=str(data["main_menu"].message_id), text="Выберете в какой раздел загружать файлы", reply_markup=Admin_Keyboards.file_loading())
            await state.update_data(inline_menu=menu)
        except KeyError:
            menu = await callback.message.answer(text="Выберете в какой раздел загружать файлы", reply_markup=Admin_Keyboards.file_loading())
            await state.update_data(inline_menu=menu)
    elif callback.data == 'delete_member':
        await callback.message.edit_text(text='Введите один или несколько user_id через запятую')
        await state.set_state(Admin_states.delete_member)








    










