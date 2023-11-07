from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton


# ----------------------------------------------U-S-E-R-T-P-A-N-E-L----------------------------------------------
class User_Keyboards():
    
    def buttons_clunge():
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

    user_starting_keyboard = buttons_clunge().adjust(1, repeat=True)
# ----------------------------------------------U-S-E-R-T-P-A-N-E-L----------------------------------------------

# ----------------------------------------------O-W-N-E-R-P-A-N-E-L----------------------------------------------

class Owner_Keyboards():

    def buttons_clunge():
        owner_starting_keyboard = InlineKeyboardBuilder()

        admin_panel = InlineKeyboardButton(text='Админ-панель', callback_data='admin_panel')
        tester_panel = InlineKeyboardButton(text='Тестер-панель', callback_data='tester_panel')
        moder_panel = InlineKeyboardButton(text='Модер-панель', callback_data='moder_panel')
        user_panel = InlineKeyboardButton(text='Юзер-панель', callback_data='user_panel')
        owner_starting_keyboard.add(admin_panel, tester_panel, moder_panel, user_panel)
        return owner_starting_keyboard
    
    owner_starting_keyboard = buttons_clunge().adjust(1, repeat=True)
# ----------------------------------------------O-W-N-E-R-P-A-N-E-L----------------------------------------------

# ----------------------------------------------A-D-M-I-N-P-A-N-E-L----------------------------------------------
class Admin_Keyboards():

    def buttons_clunge():
        admin_starting_keyboard = InlineKeyboardBuilder()

        check_registrations = InlineKeyboardButton(text='Проверить регистрацию', callback_data='check_reg')
        admin_starting_keyboard.add(check_registrations)
        return admin_starting_keyboard
    
    admin_starting_keyboard = buttons_clunge().adjust(1, repeat=True)
# ----------------------------------------------A-D-M-I-N-P-A-N-E-L----------------------------------------------

