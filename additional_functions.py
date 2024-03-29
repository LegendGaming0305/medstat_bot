from aiogram.utils.keyboard import InlineKeyboardBuilder
import json
from functools import wraps
from aiogram.utils.keyboard import InlineKeyboardBuilder
from fuzzywuzzy import fuzz
from aiogram.fsm.context import FSMContext
from aiogram import types
import pandas as pd
from db_actions import Database
from asyncio import sleep
from aiogram.exceptions import TelegramBadRequest
import datetime
from typing import List, Tuple

db = Database()

def save_to_txt(file_path: str = "", print_as_finished = True, save_mode: str = "a", **kwargs):
        
        r"""Функция save_to_txt принимает в себя:
        1) file_path - путь к файлу в формате: C:\Users\user\*file_dir*\. в случае, если нет необходимости 
        сохранять файл в конкретную директорию, то файл сохраняется в директорию скрипта с save_to_txt;
        2) print_as_finished - флаг, который контролирует вывод надписи The information has been added to the {file_name}.txt file.;
        3) save_mode - формат работы с .txt файлом, по умолчанию - 'a';
        4) **kwargs - основа функции, где key - название файла, а value - содержимое файла;
        """
        for key, value in kwargs.items():
            file_name = key
            with open(rf"{file_path}{file_name}.txt", mode=save_mode, buffering=-1, encoding="utf-8") as file:
                if isinstance(value, (tuple, list)):
                    [file.write(val) for val in value]
                else:
                    file.write(str(value))
            if print_as_finished == True:
                print("\n")
                print(f"The information has been added to the {file_name}.txt file.")
        return file

def access_block_decorator(func):
    '''
    Как работает этот декоратор:
    1. Принимается декорируемая функция так, что в обертке определяются значения quarry_type и state
    2. Далее идет проверка на текущий статус
    * Accept - Пользователю предоставляется доступ к функции
    * Pending & Decline - Декоратор сдерживает пользователя от перехода к функции
    '''

    async def async_wrapper(quarry_type, state):
        @quarry_definition_decorator
        async def inner_locker(**kwargs):
            status = await db.get_status(user_id=kwargs["user_id"]) if quarry_type or state else ...

            match status:
                case 'Accept':
                    return await func(quarry_type, state)
                case 'Pending':
                    await kwargs["answer_type"].answer(text="Ваше регистрационное заявление подтверждается! Ожидайте")
                case 'Decline':
                    await kwargs["answer_type"].answer(text="Ваша заявка отклонена и пока что у Вас нет доступа к этому разделу. Свяжитесь с администратором - @tsayushka")

        return await inner_locker(quarry_type, state)
    return async_wrapper 

def quarry_definition_decorator(func):
    """
        Как работает этот декоратор:
        1. Обертка async_wrapper принимает в себя quarry_type, state (именованные аргументы) и позиционные аргументы,
        такие, что kwargs планируется быть пустым при старте работы обертки
        2. В зависимости от типа query_type контейнер kwargs наполняется нужными переменными 
        в зависимости: ключ-значение
        3. Декорируемая функция (обязательно в условии распологающая kwargs-ом) возвращается, но уже с 
        заполненным контейнером kwargs
    """
    @wraps(func) 
    async def async_wrapper(query_type, state, **kwargs):  
                if isinstance(query_type, types.Message) == True:
                    kwargs.update({
                        "default_query": query_type,
                        "chat_id": query_type.chat.id,
                        "user_id": query_type.from_user.id,
                        "chat_type": query_type.chat.type,
                        "answer_message_type": query_type.answer,
                        "answer_type": query_type,
                        "message_id": query_type.message_id,
                        "edit_text": None
                        })
                elif isinstance(query_type, types.CallbackQuery) == True:
                    kwargs.update({
                        "default_query": query_type.message,
                        "chat_id": query_type.message.chat.id,
                        "user_id": query_type.from_user.id,
                        "chat_type": query_type.message.chat.type,
                        "answer_message_type": query_type.message.answer,
                        "answer_type": query_type,
                        "message_id": query_type.message.message_id,
                        "edit_text": query_type.message.edit_text
                        })
                return await func(**kwargs) 
    return async_wrapper    

def user_registration_decorator(func):
    from keyboards import general_kb
    ''' 
    Как работает этот декоратор:
    1. Обертка принимает query_type и state от функции, что обернута async_wrapper-ом.
    2. Далее происходит декорирование асинхронной функции registration так, что:
    - В quarry_definition_decorator поступают query_type и state;
    - В з-ти от query_type kwargs наполняется необходимыми для регистрации переменными (user_id, chat_id, answer_type и др);
    - Возвращается функция registration но уже с позиционными аргументами kwargs, которые используются далее при регистрации;
    3. Функция registration поначалу проверяет json-файл с приоритетами по user_id из kwargs,
    затем, если пользователь все ещё не идентифицирован, то автоматически он определяется как USER
    '''
    async def async_wrapper(query_type, state):
        @quarry_definition_decorator
        async def registration(**kwargs):
            from non_script_files.config import PRIORITY_LIST
            from keyboards import User_Keyboards, Owner_Keyboards, Specialist_keyboards
            prior_user = False
            backing_to_menu = await kwargs["answer_type"].answer("Успешный возврат меню...", reply_markup=general_kb)
            await state.clear()
        
            async def prior_keyboard_send(key_type: InlineKeyboardBuilder, row: str):
                from cache_container import Data_storage
                nonlocal prior_user
                for string_num in range(len(row)):
                    if row[string_num]["user_id"] == kwargs["user_id"]:
                        prior_user = True
                        await kwargs["answer_type"].answer('Меню', reply_markup=key_type)
                Data_storage.user_id = kwargs["user_id"]
                    
            for level in PRIORITY_LIST.keys():
                row = PRIORITY_LIST[level]
                
                match level:
                    case "OWNER":
                        await prior_keyboard_send(key_type=Owner_Keyboards.owner_starting_keyboard.as_markup(), row=row)
                    case "SPECIALIST":
                        await prior_keyboard_send(key_type=Specialist_keyboards.main_menu(), row=row)
                
            if prior_user == False:
                from main import db
                await db.update_user_info(user_id=kwargs['user_id'], telegram_name=kwargs['default_query'].from_user.full_name)
                status = await db.get_status(user_id=kwargs['user_id'])
                if status is None or status == 'Decline':
                    await kwargs['answer_type'].answer('Меню', reply_markup=await User_Keyboards.main_menu(False))
                elif status in ('Accept', 'Pending'):
                    await kwargs['answer_type'].answer('Меню', reply_markup=await User_Keyboards.main_menu(True, kwargs['user_id']))

            return await func(query_type, state)
        return await registration(query_type, state)
    return async_wrapper
              
def execution_count_decorator(func):
    """
    Как работает этот декоратор:
    1. Декоратор отсчитывает вызов той или иной функции
    2. Он возвращает количество вызовов
    3. Если количество вызовов = 1, а finished == True, то выходит сообщение о том, 
    что необходимо отправить публикацию как минимум один раз, для продолжения сессии
    """
    async_wrapper_counter = 0
    async def async_wrapper(*args, **kwargs):
        nonlocal async_wrapper_counter
        async_wrapper_counter += 1
        
        return await func(*args, **kwargs)
    return async_wrapper

def json_reader(path: str):
    '''Чтение json-файла и возврат значения'''
    with open(path, 'r', encoding="utf-8") as j_file:
        return json.load(j_file)
    
async def create_questions(specialist_id: int, form: str = None) -> tuple[dict]:
    '''
    Создание списка вопросов и помещения их в tuple
    '''
    if form:
        rows = await db.get_form_questions(form_name=form)
    else:
        rows = await db.get_specialits_questions(specialist_id=specialist_id)
    questions = []
    for row in rows:
    
        data = {'question': row['question_content'],
                'lp_user_id': row['lp_user_id'],
                'form_name': row['form_name'],
                'message_id': row['question_message'],
                'subject_name': row['subject_name']}
        
        questions.append(data)
    return tuple(questions)     

def fuzzy_handler(user_question: str, pattern: list):

    def extract_filtered(dictionary: dict, similarity_values: list) -> dict:
        clean_dictionary = dict()
        result = list(filter(lambda x: x >= 50, similarity_values))

        if result == []:
            return None, None
        else:
            while result != []:
                popped_element = result.pop()
                try:
                    data_for_update = list(filter(lambda x: popped_element in x[1], dictionary.items()))
                except IndexError:
                    return None, None
                clean_dictionary.update([(data_for_update[0][0], data_for_update[0][1])])

        maximum_values = list(filter(lambda x: max(similarity_values) == x[1][0], clean_dictionary.items()))

        return clean_dictionary, maximum_values

    text_orig = pattern.copy() ; text_orig = list(map(lambda x: x.lower(), text_orig))
    user_question = user_question.lower().strip()
    current_similarity_rate = 0
    dict_container = dict()

    for number, phrase in enumerate(text_orig):
        if('вопрос:' in phrase):
            pattern_question = phrase.replace('вопрос:','', 1)
            current_similarity_rate = (fuzz.token_sort_ratio(pattern_question, user_question))
            dict_container.update([(number, (current_similarity_rate, pattern_question))])

    similarity_rate_list = sorted(list({value[0] for value in dict_container.values()}))
    filtered_dictionary, maximum_values = extract_filtered(dictionary=dict_container, similarity_values=similarity_rate_list)
    
    if filtered_dictionary == None:
        return None, None
    else:
        pattern_answers = '' ; keys_seq = list(dict_container.keys())
        
        for value in maximum_values:
            value_index = keys_seq.index(value[0])
            try:
                pattern_answers = pattern_answers + ''.join(text_orig[value[0] + 1: keys_seq[value_index + 1]])
            except IndexError:
                pattern_answers = text_orig[value[0] + 1]
            pattern_answers = pattern_answers.replace('ответ:','', 1)
                    
        pattern_questions = list(filtered_dictionary.items())
        return pattern_answers, pattern_questions

def file_reader(file_path: str):
    with open(file=file_path, mode='r', buffering=-1, encoding="utf-8") as file:
        pattern_text = file.readlines()
        return pattern_text

async def question_redirect(query, state: FSMContext):
    from states import User_states
    from keyboards import User_Keyboards
    data = await state.get_data()
    user_question = data['user_question']
    
    if isinstance(query, types.Message) == True:
        await db.process_question(user_id=query.from_user.id, question=user_question, form=data['tag'], message_id=query.message_id)
    else:
        await db.process_question(user_id=query.from_user.id, question=user_question, form=data['tag'], message_id=query.message.message_id)

    await state.set_state(User_states.form_choosing)
    data = await state.get_data()

    try:
        message = await query.reply(text=f'Ваш вопрос по форме {data["form_info"]["form_name"]} передан', reply_markup=User_Keyboards.back_to_main_menu().as_markup())
        await state.update_data(notific_message=message)
    except (TelegramBadRequest, AttributeError):
        message = None

    # await state.set_state(User_states.form_choosing)

async def creating_excel_users() -> None:
    '''
    Создание excel файла с данными по зарегистрированным пользователям
    '''
    from main import db
    # person_data = await db.get_registrated_db()
    df = pd.DataFrame(await db.get_registrated_db(), columns=['id', 'user_id', 'Наименование субъекта', 
                                                              'Должность', 'Организация', 'Дата регистрации', 'Имя в телеграмме'])
    df_output = df.loc[:, ['user_id','Имя в телеграмме', 'Наименование субъекта', 'Должность', 'Организация', 'Дата регистрации']]
    df_output.to_excel('miac_output.xlsx')

def extracting_query_info(query):
    query_info = dict()

    if isinstance(query, types.Message) == True:
        
        if query.text:
            query_info['query_format'] = 'Text'
            file_id = None
        
        if query.photo:
            query_info['query_format'] = 'Photo'
            file_id = query.photo[-1]

        if query.document:
            query_info['query_format'] = 'Document'
            query_info['file_name'] = query.document.file_name
            file_id = query.document.file_id
        else:
            query_info['file_name'] = 'Null'

        if query.video:
            query_info['query_format'] = 'Video'
            file_id = query.video.file_id
        
        if query.caption:
                query_info['has_caption'] = True
                query_info['caption_text'] = query.caption
        else:
            query_info['has_caption'] = False
            query_info['caption_text'] = 'Null'
        
        return query_info, file_id
    elif isinstance(query, types.CallbackQuery) == True:

        if query.message.text:
            query_info['query_format'] = 'Text'
            file_id = None

        if query.message.photo:
            query_info['query_format'] = 'Photo'
            file_id = query.message.photo[-1]

        if query.message.document:
            query_info['query_format'] = 'Document'
            query_info['file_name'] = query.message.document.file_name
            file_id = query.message.document.file_id
        else:
            query_info['file_name'] = 'Null'

        if query.message.video:
            query_info['query_format'] = 'Video'
            file_id = query.message.video.file_id

        if query.message.caption:
                query_info['has_caption'] = True
                query_info['caption_text'] = query.message.caption
        else:
            query_info['has_caption'] = False
            query_info['caption_text'] = 'Null'

        return query_info, file_id
    
async def message_delition(*args, time_sleep = 20):
            await sleep(time_sleep)
            for arg in args:
                await arg.delete()
        
async def document_loading(button_name: str, doc_info: dict = {}):
    for doc_id, file_format in doc_info.items():
        await db.uploading_file(file_id=doc_id, button_type=button_name, upload_tuple=tuple(file_format.values()))

async def delete_member(message: str, chat_id: int):
    from main import bot
    if ',' in message:
        ids = [int(i.strip()) for i in message.split(',')]
        for id in ids:
            await bot.ban_chat_member(chat_id=chat_id,
                                      user_id=id)
    else:
        await bot.ban_chat_member(chat_id=chat_id,
                                  user_id=int(message))
        
async def choose_form(user_id: int, callback: types.CallbackQuery):
    from non_script_files.config import PRIORITY_LIST
    from keyboards import User_Keyboards
    for user in PRIORITY_LIST['OWNER']:
        if user_id in user.values():
            await callback.message.edit_text(text='Выберите форму, по которой хотите увидеть вопросы', 
                                             reply_markup=User_Keyboards.section_chose().as_markup())
            return True
    return False

async def object_type_generator(obj_type, types_array: List[Tuple[str, datetime.time]] = [], time_switch = False, force_clean = False):
    """
    Данная функция определяет то, из чего состоит запрос польователя, когда тот отправляет несколько файлов, текст и иные данные в одним сообщением.
    Т.е. фактически данная функция разделяет один комплексный запрос от другого посредством промежутка между запросами в 5 секунд.
    Для того, чтобы выключить временную зависимость данной функции используется флаг time_switch.
    Так же, для очищения локального хранилища вне зависимости от времени, используется флаг force_clean.
    """
    tdelta_sec = datetime.timedelta(seconds=5)
    dt_now = datetime.datetime.now()
    new_row = False
    types_array.append((obj_type, dt_now))
    
    if time_switch == False:
        try:
            ltd = types_array[-2][1]
            tdelta = dt_now - types_array[-2][1]
            
            if tdelta.seconds >= tdelta_sec.seconds:
                new_row = True
                types_array.clear()
                types_array.append((obj_type, dt_now))
        except IndexError:
            pass
            
        yield types_array, new_row
    else:
        if force_clean == True:
            types_array.clear()
        else:
            pass
        
        yield types_array
     

        


        

        

        

