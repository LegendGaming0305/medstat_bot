from aiogram.fsm.context import FSMContext
from aiogram import types
import json
from functools import wraps

from keyboards import *

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
    async def async_wrapper(quarry_type, state):
        if await state.get_state() == "Admin_states:registration_claim":
             await quarry_type.answer(text="Ваше регистрационное заявление подтверждается! Ожидайте.")
        else:
            return await func(quarry_type, state)
    return async_wrapper 

def quarry_definition_decorator(func):
    """
        Как работает этот декоратор:
        1. С помощью оберточной функции и именованных аргументов, заключенных в **kwargs,
        декоратор вычленяет значение переменных, что представляют собой изменяемые объекты 
        в з-ти от типа запроса: переменная вычисления message_id, переменная вычисления user_id,
        и другие;
        2. Внутри декоратора выполняется проверка на тип запроса и только затем 
        вышеуказанные переменные меняются на те, что требует тот или иной тип запроса;
        3. После перезаписи возвращается принимаемая функция, но уже с перезаписанными 
        переменными;
    """
    @wraps(func) 
    async def async_wrapper(quarry_type, state, **kwargs):             
                if isinstance(quarry_type, types.Message) == True:
                    kwargs.update({
                        "chat_id": quarry_type.chat.id,
                        "user_id": quarry_type.from_user.id,
                        "chat_type": quarry_type.chat.type,
                        "answer_type": quarry_type,
                        "message_id": quarry_type.message_id,
                        "edit_text": None
                        })
                elif isinstance(quarry_type, types.CallbackQuery) == True:
                    kwargs.update({
                        "chat_id": quarry_type.message.chat.id,
                        "user_id": quarry_type.from_user.id,
                        "chat_type": quarry_type.message.chat.type,
                        "answer_type": quarry_type.message,
                        "message_id": quarry_type.message.message_id,
                        "edit_text": quarry_type.message.edit_text
                        })
                return await func(**kwargs) 
    return async_wrapper    

def user_registration_decorator(func):
    async def async_wrapper(quarry_type, state):
        @quarry_definition_decorator
        async def registration(**kwargs):
            from non_script_files import config  
            prior_user = False

            async def prior_keyboard_send(key_type, row):
                nonlocal prior_user
                for string_num in range(len(row)):
                    if row[string_num]["user_id"] == kwargs["user_id"]:
                        prior_user = True
                        await kwargs["answer_type"].answer('Меню', reply_markup=key_type)
                    
            for level in config.PRIORITY_LIST.keys():
                row = config.PRIORITY_LIST[level]
                
                match level:
                     case "OWNER":
                        await prior_keyboard_send(key_type=Owner_Keyboards.owner_starting_keyboard.as_markup(), row=row)
                
            if prior_user == False:
                await kwargs["answer_type"].answer('Меню', reply_markup=User_Keyboards.user_starting_keyboard.as_markup())
            
            return await func(quarry_type, state)
        return await registration(quarry_type, state)
    return async_wrapper
              
def json_reader(path: str):
    with open(path, 'r', encoding="utf-8") as j_file:
        return json.load(j_file)
    
def fio_handler(fio: str):
    fio = list(map(lambda x: x.capitalize(), fio.split("")))
    fio = f"{fio[0][0]}. " + f"{fio[1][0]}. " + fio[2]
    return fio
