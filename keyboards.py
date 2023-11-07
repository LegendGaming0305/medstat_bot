from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardMarkup
from aiogram.types import InlineKeyboardButton
import asyncio as asy

from db_actions import Database
from additional_functions import fio_handler

db = Database()


# ----------------------------------------------U-S-E-R-T-P-A-N-E-L----------------------------------------------
class User_Keyboards():
    
    def main_menu():
        '''
            Функция, возвращающая все клавиатуры, связанные с главным меню и возвратом к нему.
            Не может быть аргументом reply_markup
        '''
        user_starting_keyboard = InlineKeyboardBuilder()

        npa_button = InlineKeyboardButton(text='НПА', callback_data='npa')
        medstat_button = InlineKeyboardButton(text='Медстат', callback_data='medstat')
        statistic_button = InlineKeyboardButton(text='Статистика', callback_data='statistic')
        method_recommendations_button = InlineKeyboardButton(text='Методические рекомендации', callback_data='method_recommendations')
        registration_button = InlineKeyboardButton(text='Регистрация', callback_data='registration')
        make_question_button = InlineKeyboardButton(text='Задать вопрос', callback_data='make_question')
        user_starting_keyboard.add(npa_button, 
                      medstat_button, 
                      statistic_button, 
                      method_recommendations_button, 
                      registration_button)
        
        return user_starting_keyboard

    user_starting_keyboard = main_menu().adjust(1, repeat=True)
# ----------------------------------------------U-S-E-R-T-P-A-N-E-L----------------------------------------------

# ----------------------------------------------O-W-N-E-R-P-A-N-E-L----------------------------------------------

class Owner_Keyboards():

    def main_menu():
        owner_starting_keyboard = InlineKeyboardBuilder()

        admin_panel = InlineKeyboardButton(text='Админ-панель', callback_data='admin_panel')
        tester_panel = InlineKeyboardButton(text='Тестер-панель', callback_data='tester_panel')
        moder_panel = InlineKeyboardButton(text='Модер-панель', callback_data='moder_panel')
        user_panel = InlineKeyboardButton(text='Юзер-панель', callback_data='user_panel')
        owner_starting_keyboard.add(admin_panel, tester_panel, moder_panel, user_panel)
        return owner_starting_keyboard
    
    owner_starting_keyboard = main_menu().adjust(1, repeat=True)
# ----------------------------------------------O-W-N-E-R-P-A-N-E-L----------------------------------------------

# ----------------------------------------------A-D-M-I-N-P-A-N-E-L----------------------------------------------
class Admin_Keyboards():

    def main_menu():
        '''
            Функция, возвращающая все клавиатуры, связанные с главным меню и возвратом к нему.
            Может быть аргументом reply_markup
        '''

        check_registrations = InlineKeyboardButton(text='Проверить регистрацию', callback_data='check_reg')

        admin_starting_keyboard = InlineKeyboardMarkup(inline_keyboard=[[check_registrations]])
        return admin_starting_keyboard
       
    def reg_process_keyboard(user_id):
        '''
            Функция, возвращающая все клавиатуры, связанные с процессом регистрации (с соотношением админ-->юзер)
            Может быть аргументом reply_markup
        '''
        
        back_to_checking = InlineKeyboardButton(text='Вернуться', callback_data='check_reg')
        decline = InlineKeyboardButton(text='Отклонить заявку', callback_data=f'dec_app:{user_id}')
        accept = InlineKeyboardButton(text='Принять заявку', callback_data=f'acc_app:{user_id}')

        admin_registrator_keyboard = InlineKeyboardMarkup(inline_keyboard=[[back_to_checking],
                                                                           [decline],
                                                                           [accept]])
        return admin_registrator_keyboard
    
    def application_gen(unreg_tuple):

        '''
            Отдельная функция, генерирующая кнопки, в з-ти от заявок пользователей
            Может быть аргументом reply_markup
        '''
        unique_keys, registration_forms = unreg_tuple[0], unreg_tuple[1]
        # reg_forms stands for registration_process (id, user_id, subject, name, post, phone, date)
        # unique_keys stands for (reg_process_id)
        # id = unique_keys[0][0]
        # date = registration_forms[0][6]
        # name = registration_forms[0][3]

        buttons_data = {unique_keys[i][0]: InlineKeyboardButton(text=fio_handler(registration_forms[i][3]), callback_data=f"generated_button&uk:{unique_keys[i][0]}&datetime:{registration_forms[i][6]}") for i in range(len(registration_forms))}
        generated_keyboard = InlineKeyboardMarkup(inline_keyboard=[[elem] for elem in buttons_data.values()])

        return generated_keyboard
    
# ----------------------------------------------A-D-M-I-N-P-A-N-E-L----------------------------------------------

# ----------------------------------------------G-E-N-E-R-A-L-----------------------------------------------




# ----------------------------------------------G-E-N-E-R-A-L-----------------------------------------------
