from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton

from db_actions import Database
from additional_functions import fio_handler
from cache_container import cache

db = Database()


# ----------------------------------------------U-S-E-R-T-P-A-N-E-L----------------------------------------------
class User_Keyboards():
    def main_menu(filled_form = False) -> InlineKeyboardBuilder:

        '''
            Функция, возвращающая все клавиатуры, связанные с главным меню и возвратом к нему.
            Может быть аргументом reply_markup
        '''
        user_starting_keyboard = InlineKeyboardBuilder()

        npa_button = InlineKeyboardButton(text='НПА', callback_data='npa')
        medstat_button = InlineKeyboardButton(text='Медстат', callback_data='medstat')
        statistic_button = InlineKeyboardButton(text='Статистика', callback_data='statistic')
        method_recommendations_button = InlineKeyboardButton(text='Методические рекомендации', callback_data='method_recommendations')
        registration_button = InlineKeyboardButton(text='Регистрация', callback_data='registration')
        make_question_button = InlineKeyboardButton(text='Задать вопрос', callback_data='make_question')
        
        if filled_form == False:
            user_starting_keyboard.add(npa_button, 
                        medstat_button, 
                        statistic_button, 
                        method_recommendations_button, 
                        registration_button)
        else:
            user_starting_keyboard.add(npa_button, 
                        medstat_button, 
                        statistic_button, 
                        method_recommendations_button, 
                        make_question_button)
        
        return user_starting_keyboard.adjust(1, repeat=True)
    
    def section_chose() -> InlineKeyboardBuilder:
        section_key = InlineKeyboardBuilder()

        button_one = InlineKeyboardButton(text='• Ф. № 30 Латышова А.А.', callback_data='sec_one')
        button_two = InlineKeyboardButton(text='• Ф. № 30 Тюрина Е.М.', callback_data='sec_two')
        button_three = InlineKeyboardButton(text='• Ф. № 30 Шелепова Е.А.', callback_data='sec_three')
        button_four = InlineKeyboardButton(text='• Ф. № 14-ДС; Ф. 30 (в части работы СМП) Шляфер С.И.', callback_data='sec_four')
        button_five = InlineKeyboardButton(text='• Ф. № 47', callback_data='sec_five')
        button_six = InlineKeyboardButton(text='• ф. № 8, 33, 2-ТБ, 7-ТБ, 8-ТБ, 10-ТБ (туберкулез);', callback_data='sec_six')
        button_seven = InlineKeyboardButton(text='• Ф. № 12, 12-село', callback_data='sec_seven')
        button_eight = InlineKeyboardButton(text='• Ф. № 14, 19, 41, 54, 16-ВН, 1-РБ, 1-Дети (здрав), 32, 232(вкладыш), 53, 70', callback_data='sec_eight')
        button_nine = InlineKeyboardButton(text='• Специализированные формы (№ 7, 9, 34; Ф. № 10, 36; Ф. № 36 -ПЛ; Ф. № 11, 37; Ф. № 13; Ф. № 15; Ф. № 55, 56; Ф. № 57; Ф. № 61; Ф. № 64 ; Ф. № 30 (в части работы Лабораторной службы)', callback_data='sec_nine')
        button_ten = InlineKeyboardButton(text='Чат координаторов', callback_data='sec_ten')

        section_key.add(button_one, button_two, button_three, button_four, 
                        button_five, button_six, button_seven, button_eight,
                        button_nine, button_ten)
        
        return section_key.adjust(1, repeat=True)

# ----------------------------------------------U-S-E-R-T-P-A-N-E-L----------------------------------------------

# ----------------------------------------------O-W-N-E-R-P-A-N-E-L----------------------------------------------

class Owner_Keyboards():

    def main_menu() -> InlineKeyboardBuilder:
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

    def main_menu() -> InlineKeyboardBuilder:
        '''
            Функция, возвращающая все клавиатуры, связанные с главным меню и возвратом к нему.
            Может быть аргументом reply_markup
        '''
        admin_starting_keyboard = InlineKeyboardBuilder()

        check_registrations = InlineKeyboardButton(text='Проверить регистрацию', callback_data='check_reg')

        admin_starting_keyboard.add(check_registrations)
        return admin_starting_keyboard.as_markup()
       
    def reg_process_keyboard(user_id, user_string_id) -> InlineKeyboardBuilder:
        '''
            Функция, возвращающая все клавиатуры, связанные с процессом регистрации (с соотношением админ-->юзер)
            Может быть аргументом reply_markup
        '''
        admin_registrator_keyboard = InlineKeyboardBuilder()
        
        back_to_checking = InlineKeyboardButton(text='Вернуться', callback_data='check_reg')
        decline = InlineKeyboardButton(text='Отклонить заявку', callback_data=f'dec_app:{user_id}:{user_string_id}')
        accept = InlineKeyboardButton(text='Принять заявку', callback_data=f'acc_app:{user_id}:{user_string_id}')

        admin_registrator_keyboard.add(accept, decline,
                                       back_to_checking)
        admin_registrator_keyboard.adjust(2, 1)

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
        generated_keyboard = InlineKeyboardBuilder()
        buttons_data = [InlineKeyboardButton(text=fio_handler(registration_forms[i][3]), callback_data=f"generated_button&uk:{unique_keys[i][0]}&datetime:{registration_forms[i][6]}") for i in range(len(registration_forms))]
        generated_keyboard.add(*[elem for elem in buttons_data])
        generated_keyboard.adjust(3, repeat=True)

        return generated_keyboard
    
# ----------------------------------------------A-D-M-I-N-P-A-N-E-L----------------------------------------------

# ----------------------------------------------G-E-N-E-R-A-L-----------------------------------------------




# ----------------------------------------------G-E-N-E-R-A-L-----------------------------------------------
