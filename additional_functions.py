from aiogram.fsm.context import FSMContext
import json

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

def json_reader(path):
    with open(path, 'r', encoding="utf-8") as j_file:
        return json.load(j_file)
        
