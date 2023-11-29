from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
import numpy as np

from db_actions import Database
from additional_functions import fio_handler

db = Database()

back_to_menu = [[KeyboardButton(text="Возврат в главное меню")]]
general_kb = ReplyKeyboardMarkup(keyboard=back_to_menu, resize_keyboard=True)
BUTTONS_TO_REMOVE = {'private':0, 'form':1, 'open':2, '0':'private', '1':'form', '2':'open'}

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
    
    def back_to_main_menu() -> InlineKeyboardBuilder:
        main_menu_back = InlineKeyboardBuilder()
        back_button = InlineKeyboardButton(text='Вернуться в главное меню', callback_data='main_menu')
        main_menu_back.add(back_button)
        return main_menu_back.adjust(1, repeat=True)

    def section_chose() -> InlineKeyboardBuilder:
        section_key = InlineKeyboardBuilder()

        button_one = InlineKeyboardButton(text='• Ф. № 30 Латышова А.А.', callback_data='sec_one')
        button_two = InlineKeyboardButton(text='• Ф. № 30 Тюрина Е.М.', callback_data='sec_two')
        button_three = InlineKeyboardButton(text='• Ф. № 30 Шелепова Е.А.', callback_data='sec_three')
        button_four = InlineKeyboardButton(text='• Ф. № 14-ДС; Ф. 30 (в части работы СМП) Шляфер С.И.', callback_data='sec_four')
        button_five = InlineKeyboardButton(text='• Ф. № 47', callback_data='sec_five')
        button_six = InlineKeyboardButton(text='• ф. № 8, 33, 2-ТБ, 7-ТБ, 8-ТБ, 10-ТБ (туберкулез)', callback_data='sec_six')
        button_seven = InlineKeyboardButton(text='• Ф. № 12, 12-село', callback_data='sec_seven')
        button_eight = InlineKeyboardButton(text='• Ф. № 14, 19, 41, 54, 16-ВН, 1-РБ, 1-Дети (здрав), 32, 232(вкладыш), 53, 70', callback_data='sec_eight')
        button_nine = InlineKeyboardButton(text='• Специализированные формы (№ 7, 9, 34; Ф. № 10, 36; Ф. № 36 -ПЛ; Ф. № 11, 37; Ф. № 13; Ф. № 15; Ф. № 55, 56; Ф. № 57; Ф. № 61; Ф. № 64 ; Ф. № 30 (в части работы Лабораторной службы)', callback_data='sec_nine')
        button_ten = InlineKeyboardButton(text='Чат координаторов', callback_data='sec_ten')
        button_eleven = InlineKeyboardButton(text='• Нормативные документы', callback_data='sec_eleven')
        button_medstat = InlineKeyboardButton(text='• Система МЕДСТАТ', callback_data='sec_medstat')
        button_general = InlineKeyboardButton(text='• Общий раздел', callback_data='sec_general')

        section_key.add(button_eleven, button_medstat, button_general, button_one, button_two, button_three, 
                        button_four, button_five, button_six, button_seven, button_eight,
                        button_nine, button_ten)
        
        return section_key.adjust(1, repeat=True)

    async def create_district_buttons() -> InlineKeyboardBuilder:
        '''
        Создание клавиатуры для выбора Федерального округа
        '''
        district_keyboard = InlineKeyboardBuilder()
        from main import db
        result = await db.get_miac_information(info_type='federal_district')
        for record in result:
            federal_name = record['federal_name']
            district_tag = record['district_tag']
            button = InlineKeyboardButton(text=federal_name, callback_data=district_tag)
            district_keyboard.add(button)

        district_keyboard.adjust(1, repeat=True)
        return district_keyboard.as_markup()
    
    async def create_regions_buttons(district_id: int) -> InlineKeyboardBuilder:
        region_keyboard = InlineKeyboardBuilder()
        from main import db
        result = await db.get_miac_information(info_type='region', district_id=district_id)
        for record in result:
            region_name = record['region_name']
            region_tag = record['region_tag']
            button = InlineKeyboardButton(text=region_name, callback_data=region_tag)
            region_keyboard.add(button)

        region_keyboard.adjust(1, repeat=True)
        return region_keyboard.as_markup()
    
    def fuzzy_buttons_generate(questions) -> InlineKeyboardBuilder:
        text_pattern = []
        fuzzy_keyboard = InlineKeyboardBuilder()
        buttons_data = [InlineKeyboardButton(text=f"Ответ на вопрос №{num + 1}", callback_data=f"fuzzy_buttons&simular_rate:{value[1][0]}&index:{value[0]}") for num, value in enumerate(questions)]
        [text_pattern.append(f"Вопрос №{num + 1}: {value[1][1]}\n") for num, value in enumerate(questions)]
        text_pattern = "".join(text_pattern)
        fuzzy_keyboard.add(*[elem for elem in buttons_data])
        fuzzy_keyboard.adjust(1, repeat=True)
        return fuzzy_keyboard, text_pattern

    def back_to_fuzzy_questions() -> InlineKeyboardBuilder:
        back_to_pool = InlineKeyboardBuilder()
        back_to_pool.add(InlineKeyboardButton(text="Назад к списку вопросов", callback_data="back_to_fuzzy"))
        back_to_pool.adjust(1, repeat=True)
        return back_to_pool

    def out_of_fuzzy_questions() -> ReplyKeyboardMarkup:
        
        kb = [[KeyboardButton(text="Возврат в главное меню")],
              [KeyboardButton(text="Не нашёл подходящего вопроса")]]
        out_of_pool = ReplyKeyboardMarkup(keyboard=kb,
                                        resize_keyboard=True)
        return out_of_pool

# ----------------------------------------------U-S-E-R-T-P-A-N-E-L----------------------------------------------

# ----------------------------------------------O-W-N-E-R-P-A-N-E-L----------------------------------------------

class Owner_Keyboards():

    def main_menu() -> InlineKeyboardBuilder:
        owner_starting_keyboard = InlineKeyboardBuilder()

        admin_panel = InlineKeyboardButton(text='Админ-панель', callback_data='admin_panel')
        # tester_panel = InlineKeyboardButton(text='Тестер-панель', callback_data='tester_panel')
        user_panel = InlineKeyboardButton(text='Юзер-панель', callback_data='user_panel')
        specialist_panel = InlineKeyboardButton(text='Специалист-панель', callback_data='specialist_panel')
        owner_starting_keyboard.add(admin_panel, user_panel, specialist_panel)
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
        generated_keyboard = InlineKeyboardBuilder()
        buttons_data = [InlineKeyboardButton(text=fio_handler(registration_forms[i][3]), callback_data=f"generated_button&uk:{unique_keys[i][0]}&datetime:{registration_forms[i][6]}") for i in range(len(registration_forms))]
        generated_keyboard.add(*[elem for elem in buttons_data])
        generated_keyboard.adjust(3, repeat=True)

        return generated_keyboard
    
# ----------------------------------------------A-D-M-I-N-P-A-N-E-L----------------------------------------------

# ----------------------------------------------G-E-N-E-R-A-L-----------------------------------------------

# ----------------------------------------------G-E-N-E-R-A-L-----------------------------------------------

# -----------------------------------------S-P-E-C-I-A-L-I-S-T-P-A-N-E-L----------------------------------------------
class Specialist_keyboards():

    # async def create_inline_keyboard(specialist_id: int) -> InlineKeyboardBuilder:
    # # from main import db
    #     questions_keyboard = InlineKeyboardBuilder()
    #     rows = await db.get_specialits_questions(specialist_id=specialist_id)
    #     for row in rows:
    #         question_info = list(row.values())
        
    #         data = {'question': question_info[1],
    #                 'lp_user_id': question_info[2],
    #                 'form_name': question_info[3]}
    #         # Переводим данные в json формат
    #         serialized_data = json.dumps(data)
    #         # Сохраняем в кэш память
    #         await cache.set(question_info[0], serialized_data)
    #         button = InlineKeyboardButton(text=f'Вопрос {question_info[0]}', callback_data=f'question:{question_info[0]}')
    #         questions_keyboard.add(button)
    #     questions_keyboard.adjust(3, repeat=True)
    #     return questions_keyboard.as_markup()

    def questions_gen() -> InlineKeyboardBuilder:
        '''
        Создание кнопок вопросов для специалиста
        '''
        specialist_starting_keyboard = InlineKeyboardBuilder()

        answer_the_question = InlineKeyboardButton(text='Ответить на вопросы', callback_data='answer_the_question')

        specialist_starting_keyboard.add(answer_the_question)
        specialist_starting_keyboard.adjust(1)
        return specialist_starting_keyboard.as_markup()
    
    def question_buttons(condition: str = None) -> InlineKeyboardBuilder:
        '''
        Создание кнопок для взаимодействия с вопросом
        '''
        question_keyboard = InlineKeyboardBuilder()
        if condition == None:
            choose_button = InlineKeyboardButton(text='Выбрать вопрос', callback_data=f'choose_question')
            close_button = InlineKeyboardButton(text='Закрыть вопрос', callback_data=f'close_question')
            check_history = InlineKeyboardButton(text='История диалога', callback_data=f'dialogue_history')
            question_keyboard.add(choose_button, close_button, check_history)
            question_keyboard.adjust(2)
            return question_keyboard.as_markup()
        elif isinstance(condition, tuple) == True:
            if condition[2] == 0 and condition[1] == 4:
                back_to_question = InlineKeyboardButton(text='Вернуться к вопросу', callback_data=f'back_to_question:{condition[0]}')
                next_page = InlineKeyboardButton(text="Следующая страница", callback_data=f"dialogue_history-limit:4&offset:4")
                question_keyboard.add(back_to_question, next_page)
                question_keyboard.adjust(1)
                return question_keyboard.as_markup()
            elif condition[2] != 0 and condition[1] == 4:
                back_to_question = InlineKeyboardButton(text='Вернуться к вопросу', callback_data=f'back_to_question:{condition[0]}')
                next_page = InlineKeyboardButton(text="Следующая страница", callback_data=f"dialogue_history-limit:4&offset:{condition[2] + 4}")
                prev_page = InlineKeyboardButton(text="Предыдущая страница", callback_data=f"dialogue_history-limit:4&offset:{condition[2] - 4}")
                question_keyboard.add(back_to_question, next_page, prev_page)
                question_keyboard.adjust(1)
                return question_keyboard.as_markup()
            elif condition[2] != 0 and condition[1] < 4:
                back_to_question = InlineKeyboardButton(text='Вернуться к вопросу', callback_data=f'back_to_question:{condition[0]}')
                prev_page = InlineKeyboardButton(text="Предыдущая страница", callback_data=f"dialogue_history-limit:4&offset:{condition[2] - 4}")
                question_keyboard.add(back_to_question, prev_page)
                question_keyboard.adjust(1)
                return question_keyboard.as_markup()
            elif condition[2] == 0 and condition[1] < 4:
                back_to_question = InlineKeyboardButton(text='Вернуться к вопросу', callback_data=f'back_to_question:{condition[0]}')
                question_keyboard.add(back_to_question)
                question_keyboard.adjust(1)
                return question_keyboard.as_markup()
            
    def publication_buttons(form_type: str, found_patterns: tuple = ()) -> InlineKeyboardBuilder:
        from keyboards import BUTTONS_TO_REMOVE
        '''
        Данная функция принимает в себя обязательный аргумент form_type, за который закрепляется имя формы,
        а так же необязательные позиционные аргументы *args что представляют из себя 
        кнопки, которые необходимо выключить.
        Планируется, что в 
        '''
        public_kb = InlineKeyboardBuilder()
        if found_patterns == ():
            private_chat = InlineKeyboardButton(text="В личные сообщения пользователю", callback_data="private_message")
            section_chat = InlineKeyboardButton(text=f"В раздел формы {form_type}", callback_data=f"form_type:{form_type}")
            open_channel = InlineKeyboardButton(text="В открытый канал", callback_data="open_channel")
            finish_redirectiong = InlineKeyboardButton(text="Вернуться к вопросам", callback_data="finish_state")
            public_kb.add(private_chat, section_chat, open_channel, finish_redirectiong)
            public_kb.adjust(1)
            return public_kb.as_markup()
        else:
            buttons_dict = {
                'private': InlineKeyboardButton(text="В личные сообщения пользователю", callback_data="private_message"),
                'form': InlineKeyboardButton(text=f"В раздел формы {form_type}", callback_data=f"form_type:{form_type}"),
                'open': InlineKeyboardButton(text="В открытый канал", callback_data="open_channel")
            }
            found_patterns = np.array([BUTTONS_TO_REMOVE.get(elem) for elem in found_patterns])
            keys = np.array([BUTTONS_TO_REMOVE.get(elem) for elem in buttons_dict.keys()])
            result = keys[keys != found_patterns]
            result = list(BUTTONS_TO_REMOVE.get(f'{elem}') for elem in result) ; result = list(buttons_dict.get(elem) for elem in result)

            public_kb.add(*result)
            finish_redirectiong = InlineKeyboardButton(text="Вернуться к вопросам", callback_data="finish_state")
            public_kb.add(finish_redirectiong)
            public_kb.adjust(1)
            return public_kb.as_markup()


        

        


# -----------------------------------------S-P-E-C-I-A-L-I-S-T-P-A-N-E-L----------------------------------------------
