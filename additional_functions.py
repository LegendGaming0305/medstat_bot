from aiogram import types
import json
from functools import wraps

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

def access_block_decorator(func):
    '''
    Как работает этот декоратор:
    1. Принимается декорируемая функция так, что в обертке определяются значения quarry_type и state
    2. Далее идет проверка на текущий статус - если он равен Admin_states:registration_claim, то юзеру 
    запрещен доступ к декорируемой функции
    Это не будет работать на проверке статусов. Так как у каждого юзера уникален и ты не сможешь его поставить удаленно
    определенный статус без взаимодействия юзера с ботом
    '''
    async def async_wrapper(quarry_type, state):
        if await state.get_state() == "Admin_states:registration_claim":
            await quarry_type.answer(text="Ваше регистрационное заявление подтверждается! Ожидайте")
        elif await state.get_state() == "User_states:registration_accepted":
            await quarry_type.answer(text="Вы успешно зашли")
            return await func(quarry_type, state)
        else:
            return await func(quarry_type, state)
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
                        "chat_id": query_type.chat.id,
                        "user_id": query_type.from_user.id,
                        "chat_type": query_type.chat.type,
                        "answer_type": query_type,
                        "message_id": query_type.message_id,
                        "edit_text": None
                        })
                elif isinstance(query_type, types.CallbackQuery) == True:
                    kwargs.update({
                        "chat_id": query_type.message.chat.id,
                        "user_id": query_type.from_user.id,
                        "chat_type": query_type.message.chat.type,
                        "answer_type": query_type.message,
                        "message_id": query_type.message.message_id,
                        "edit_text": query_type.message.edit_text
                        })
                return await func(**kwargs) 
    return async_wrapper    

def user_registration_decorator(func):
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
            from keyboards import User_Keyboards, Owner_Keyboards
            prior_user = False

            async def prior_keyboard_send(key_type, row):
                nonlocal prior_user
                for string_num in range(len(row)):
                    if row[string_num]["user_id"] == kwargs["user_id"]:
                        prior_user = True
                        await kwargs["answer_type"].answer('Меню', reply_markup=key_type)
                    
            for level in PRIORITY_LIST.keys():
                row = PRIORITY_LIST[level]
                
                match level:
                     case "OWNER":
                        await prior_keyboard_send(key_type=Owner_Keyboards.owner_starting_keyboard.as_markup(), row=row)
                
            if prior_user == False:
                from main import db
                status = await db.check_status(kwargs['user_id'])
                if status is None or status == 'Decline':
                    await kwargs['answer_type'].answer('Меню', reply_markup=User_Keyboards.main_menu(False).as_markup())
                elif status in ('Accept', 'Pending'):
                    await kwargs['answer_type'].answer('Меню', reply_markup=User_Keyboards.main_menu(True).as_markup())
                    

            return await func(query_type, state)
        return await registration(query_type, state)
    return async_wrapper
              
def json_reader(path: str):
    '''Чтение json-файла и возврат значения'''
    with open(path, 'r', encoding="utf-8") as j_file:
        return json.load(j_file)
    
def fio_handler(fio: str) -> str:
    '''
        Обратка фио для придания ему вида: И.И.Иванов
    '''
    fio = list(map(lambda x: x.capitalize(), fio.split(" ")))
    fio = f"{fio[0][0]}. " + f"{fio[1][0]}. " + fio[2]
    return fio
