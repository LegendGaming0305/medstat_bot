from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup

from non_script_files.config import FORMS, OPEN_CHANNEL_URL
from db_actions import Database


db = Database()

back_to_menu = [[KeyboardButton(text="Возврат в главное меню")]]
general_kb = ReplyKeyboardMarkup(keyboard=back_to_menu, resize_keyboard=True)
BUTTONS_TO_NUMBER = {'private':0, 'form':1, 'open':2}

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
        registration_button = InlineKeyboardButton(text='Регистрация для МИАЦ', callback_data='registration')
        make_question_button = InlineKeyboardButton(text='Задать вопрос', callback_data='make_question')
        open_chat_button = InlineKeyboardButton(text='Открытый канал', callback_data='link_open_chat', url=OPEN_CHANNEL_URL)
        razdel_chat_button = InlineKeyboardButton(text='Канал раздела форм', callback_data='link_razdel_chat')
        
        if filled_form == False:
            user_starting_keyboard.add(npa_button, 
                        medstat_button, 
                        statistic_button,
                        method_recommendations_button,
                        open_chat_button, 
                        registration_button)
        else:
            user_starting_keyboard.add(npa_button, 
                        medstat_button, 
                        statistic_button,
                        method_recommendations_button,
                        open_chat_button,
                        make_question_button,
                        razdel_chat_button)
        
        return user_starting_keyboard.adjust(1, repeat=True)
    
    def back_to_main_menu() -> InlineKeyboardBuilder:
        main_menu_back = InlineKeyboardBuilder()
        back_button = InlineKeyboardButton(text='Вернуться в главное меню', callback_data='main_menu')
        main_menu_back.add(back_button)
        return main_menu_back.adjust(1, repeat=True)

    def section_chose(tag_tuple: tuple = None, user_type: str = "User") -> InlineKeyboardBuilder:
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

        button_tuple = (button_one, button_two, button_three, button_four, button_five, button_six, button_seven, button_eight,
                        button_nine, button_ten, button_eleven, button_medstat, button_general)
        
        if user_type == "Admin":
            [section_key.add(button_elem) for tag_tuple_elem in tag_tuple for button_elem in button_tuple if button_elem.callback_data == tag_tuple_elem]
        else:
            section_key.add(button_eleven, button_medstat, button_general, button_one, button_two, button_three, 
                        button_four, button_five, button_six, button_seven, button_eight,
                        button_nine, button_ten)
        
        return section_key.adjust(1, repeat=True)

    async def create_district_buttons() -> InlineKeyboardMarkup:
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
    
    async def create_regions_buttons(district_id: int) -> InlineKeyboardMarkup:
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

    def out_of_fuzzy_questions() -> InlineKeyboardMarkup:
        
        out_of_pool = InlineKeyboardBuilder()
        not_found = InlineKeyboardButton(text="Не нашёл подходящего вопроса", callback_data="not_found_question")
        out_of_pool.add(not_found)
        out_of_pool.adjust(1)
        return out_of_pool.as_markup()
    
    def show_files() -> InlineKeyboardMarkup:
        show_keyboard = InlineKeyboardBuilder()
        week_button = InlineKeyboardButton(text='За последнюю неделю', callback_data='1 week')
        full_button = InlineKeyboardButton(text='За все время', callback_data='full')
        show_keyboard.add(week_button, full_button)
        show_keyboard.adjust(1)
        return show_keyboard.as_markup()

# ----------------------------------------------U-S-E-R-T-P-A-N-E-L----------------------------------------------

# ----------------------------------------------O-W-N-E-R-P-A-N-E-L----------------------------------------------

class Owner_Keyboards():

    def main_menu() -> InlineKeyboardBuilder:
        owner_starting_keyboard = InlineKeyboardBuilder()

        admin_panel = InlineKeyboardButton(text='Админ-панель', callback_data='admin_panel')
        specialist_panel = InlineKeyboardButton(text='Специалист-панель', callback_data='specialist_panel')
        owner_starting_keyboard.add(admin_panel, specialist_panel)
        return owner_starting_keyboard
    
    owner_starting_keyboard = main_menu().adjust(1, repeat=True)
# ----------------------------------------------O-W-N-E-R-P-A-N-E-L----------------------------------------------

# ----------------------------------------------A-D-M-I-N-P-A-N-E-L----------------------------------------------
class Admin_Keyboards():

    def main_menu() -> InlineKeyboardMarkup:
        '''
            Функция, возвращающая все клавиатуры, связанные с главным меню и возвратом к нему.
            Может быть аргументом reply_markup
        '''
        admin_starting_keyboard = InlineKeyboardBuilder()

        check_registrations = InlineKeyboardButton(text='Проверить регистрацию', callback_data='check_reg')
        registration_db = InlineKeyboardButton(text='Данные о зарегистрированных', callback_data='registration_db')
        publications = InlineKeyboardButton(text='Проверить публикации', callback_data='publications')
        open_chan = InlineKeyboardButton(text="Открытый канал", callback_data='op_channel_join', url="https://t.me/+11PBfYkF3Fs0OTIy")
        coord_chat = InlineKeyboardButton(text='Чат координаторов', callback_data='coord_chat_join', url="https://t.me/+zbz0lQoK6Fo2NjBi")
        sections = InlineKeyboardButton(text="Разделы форм", callback_data='sections_join', url="https://t.me/+cNQvBD_FWpQxZWRi")
        file_button = InlineKeyboardButton(text="Загрузить файлы", callback_data='load_file')
        delete_member = InlineKeyboardButton(text='Удалить пользователя из чата', callback_data='delete_member')

        admin_starting_keyboard.add(check_registrations,
                                    registration_db,
                                    publications,
                                    open_chan,
                                    coord_chat,
                                    sections,
                                    file_button,
                                    delete_member)
        admin_starting_keyboard.adjust(1, repeat=True)
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
    
    def application_gen(unreg_tuple, page_value: int):

        '''
            Отдельная функция, генерирующая кнопки, в з-ти от заявок пользователей
            Может быть аргументом reply_markup
        '''

        if page_value == 1 and len(unreg_tuple[1]) == 10:
            unique_keys, registration_forms = unreg_tuple[0], unreg_tuple[1]
            generated_keyboard = InlineKeyboardBuilder()
            buttons_data_1 = [InlineKeyboardButton(text=f"Пользователь из {registration_forms[i]['region_name']}", callback_data=f"generated_button&uk:{registration_forms[i]['id']}&datetime:{registration_forms[i]['registration_date']}") for i in range(len(registration_forms))]
            buttons_data_1 = [InlineKeyboardButton(text=f"Пользователь из {registration_forms[i]['region_name']}", callback_data=f"generated_button&uk:{registration_forms[i]['id']}&datetime:{registration_forms[i]['registration_date']}") for i in range(len(registration_forms))]
            next_page = InlineKeyboardButton(text="Следующая страница", callback_data=f"next_page:{page_value + 1}")
            generated_keyboard.add(*[elem for elem in buttons_data_1], next_page)
            generated_keyboard.add(*[elem for elem in buttons_data_1], next_page)
            generated_keyboard.adjust(1, repeat=True)

            return generated_keyboard
        elif page_value == 1 and len(unreg_tuple[1]) < 10:
            unique_keys, registration_forms = unreg_tuple[0], unreg_tuple[1]
            generated_keyboard = InlineKeyboardBuilder()
            buttons_data_2 = [InlineKeyboardButton(text=f"Пользователь из {registration_forms[i]['region_name']}", callback_data=f"generated_button&uk:{registration_forms[i]['id']}&datetime:{registration_forms[i]['registration_date']}") for i in range(len(registration_forms))]
            generated_keyboard.add(*[elem for elem in buttons_data_2])
            buttons_data_2 = [InlineKeyboardButton(text=f"Пользователь из {registration_forms[i]['region_name']}", callback_data=f"generated_button&uk:{registration_forms[i]['id']}&datetime:{registration_forms[i]['registration_date']}") for i in range(len(registration_forms))]
            generated_keyboard.add(*[elem for elem in buttons_data_2])
            generated_keyboard.adjust(1, repeat=True)

            return generated_keyboard
        elif page_value > 1 and len(unreg_tuple[1]) < 10:
            unique_keys, registration_forms = unreg_tuple[0], unreg_tuple[1]
            generated_keyboard = InlineKeyboardBuilder()
            buttons_data_3 = [InlineKeyboardButton(text=f"Пользователь из {registration_forms[i]['region_name']}", callback_data=f"generated_button&uk:{registration_forms[i]['id']}&datetime:{registration_forms[i]['registration_date']}") for i in range(len(registration_forms))]
            buttons_data_3 = [InlineKeyboardButton(text=f"Пользователь из {registration_forms[i]['region_name']}", callback_data=f"generated_button&uk:{registration_forms[i]['id']}&datetime:{registration_forms[i]['registration_date']}") for i in range(len(registration_forms))]
            prev_page = InlineKeyboardButton(text="Предыдущая страница", callback_data=f"prev_page:{page_value - 1}")
            generated_keyboard.add(*[elem for elem in buttons_data_3], prev_page)
            generated_keyboard.add(*[elem for elem in buttons_data_3], prev_page)
            generated_keyboard.adjust(1, repeat=True)
    
            return generated_keyboard
        else:
            unique_keys, registration_forms = unreg_tuple[0], unreg_tuple[1]
            generated_keyboard = InlineKeyboardBuilder()
            buttons_data_4 = [InlineKeyboardButton(text=f"Пользователь из {registration_forms[i]['region_name']}", callback_data=f"generated_button&uk:{registration_forms[i]['id']}&datetime:{registration_forms[i]['registration_date']}") for i in range(len(registration_forms))]
            buttons_data_4 = [InlineKeyboardButton(text=f"Пользователь из {registration_forms[i]['region_name']}", callback_data=f"generated_button&uk:{registration_forms[i]['id']}&datetime:{registration_forms[i]['registration_date']}") for i in range(len(registration_forms))]
            next_page = InlineKeyboardButton(text="Следующая страница", callback_data=f"next_page:{page_value + 1}")
            prev_page = InlineKeyboardButton(text="Предыдущая страница", callback_data=f"prev_page:{page_value - 1}")
            generated_keyboard.add(*[elem for elem in buttons_data_4], next_page, prev_page)
            generated_keyboard.add(*[elem for elem in buttons_data_4], next_page, prev_page)
            generated_keyboard.adjust(1, repeat=True)
    
            return generated_keyboard

    def post_publication(post_id: int, pub_type: str = 'text') -> InlineKeyboardBuilder:
        '''
        Клавиатура для выбора публикации в открытом канале
        '''
        publication_keyboard = InlineKeyboardBuilder()

        accept_post = InlineKeyboardButton(text='Опубликовать', callback_data=f'accept_post&pub_type:{pub_type}&pub_id:{post_id}')
        decline_post = InlineKeyboardButton(text='Не опубликовывать', callback_data=f'decline_post&pub_type:{pub_type}&pub_id:{post_id}')

        publication_keyboard.add(accept_post, decline_post)
        publication_keyboard.adjust(2)

        return publication_keyboard.as_markup()

    def pub_refresh():
        pub_ref_kb = InlineKeyboardBuilder()
        pub_ref_kb.add(InlineKeyboardButton(text='Проверить публикации', callback_data='publications'))
        pub_ref_kb.adjust(1)
        return pub_ref_kb.as_markup()

    def file_loading(cancel = False, history_check = False) -> InlineKeyboardBuilder():
        file_kb = InlineKeyboardBuilder()
        if cancel == False:
            npa_button = InlineKeyboardButton(text='НПА', callback_data='npa')
            medstat_button = InlineKeyboardButton(text='Медстат', callback_data='medstat')
            statistic_button = InlineKeyboardButton(text='Статистика', callback_data='statistic')
            method_recommendations_button = InlineKeyboardButton(text='Методические рекомендации', callback_data='method_recommendations')
            file_kb.add(npa_button, medstat_button, statistic_button, method_recommendations_button)
            file_kb.adjust(1)
            return file_kb.as_markup()
        else:

            cancel = InlineKeyboardButton(text="Завершить загрузку", callback_data="cancel_loading")
            check = InlineKeyboardButton(text="Посмотреть загруженные файлы", callback_data="check_loaded")
            file_kb.add(cancel, check)
            file_kb.adjust(1)
            return file_kb.as_markup()
        
    def delete_in_chat() -> InlineKeyboardMarkup:
        delete_keyboard = InlineKeyboardBuilder()

        coord = InlineKeyboardButton(text='Чат координаторов', callback_data='coord_chat')
        forms = InlineKeyboardButton(text='Раздел форм', callback_data='forms_chat')

        delete_keyboard.add(coord, forms)
        delete_keyboard.adjust(1)
        return delete_keyboard.as_markup()

# ----------------------------------------------A-D-M-I-N-P-A-N-E-L----------------------------------------------

# ----------------------------------------------G-E-N-E-R-A-L-----------------------------------------------

# ----------------------------------------------G-E-N-E-R-A-L-----------------------------------------------

# -----------------------------------------S-P-E-C-I-A-L-I-S-T-P-A-N-E-L----------------------------------------------
class Specialist_keyboards():

    def main_menu() -> InlineKeyboardBuilder:
        main_menu_kb = InlineKeyboardBuilder()

        unanswered_questions = InlineKeyboardButton(text='Ответить на вопросы', callback_data='answer_the_question:unanswered')
        answered_questions = InlineKeyboardButton(text='Вывести отвеченные вопросы', callback_data='answer_the_question:answered')
        upload_file = InlineKeyboardButton(text='Отправить файл\\сообщение', callback_data='complex_upload')
        main_menu_kb.add(unanswered_questions, answered_questions, upload_file)
        main_menu_kb.adjust(1)
        return main_menu_kb.as_markup()
    
    def sending_process() -> InlineKeyboardBuilder:
        sending_kb = InlineKeyboardBuilder()
        sending_kb.add(InlineKeyboardButton(text='Отменить отправку', callback_data='specialist_panel'))
        sending_kb.adjust(1)
        return sending_kb

    def questions_gen(flag = False, in_the_section: str = None) -> InlineKeyboardBuilder:
        '''
        Создание кнопок вопросов для специалиста
        '''
        specialist_starting_keyboard = InlineKeyboardBuilder()

        unanswered_questions = InlineKeyboardButton(text='Ответить на вопросы', callback_data='answer_the_question:unanswered') if in_the_section == None else InlineKeyboardButton(text='Ответить на вопросы', callback_data=f'admin:{in_the_section}')
        answered_questions = InlineKeyboardButton(text='Вывести отвеченные вопросы', callback_data='answer_the_question:answered') if in_the_section == None else InlineKeyboardButton(text='Вывести отвеченные вопросы', callback_data=f'admin:{in_the_section}')
        
        if flag == False:
            specialist_starting_keyboard.add(unanswered_questions)
            specialist_starting_keyboard.add(InlineKeyboardButton(text="Вернуться к формам", callback_data="admin:back_unanswered")) if in_the_section != None else None
        else:
            specialist_starting_keyboard.add(answered_questions)
            specialist_starting_keyboard.add(InlineKeyboardButton(text="Вернуться к формам", callback_data="admin:back_answered")) if in_the_section != None else None

        specialist_starting_keyboard.adjust(1)
        return specialist_starting_keyboard.as_markup()
    
    def question_buttons(condition: str = None) -> InlineKeyboardMarkup:
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
            
    def publication_buttons(spec_forms = None, found_patterns: tuple = (), file_type: str = 'message', passed_forms_info = FORMS) -> InlineKeyboardBuilder:
        '''
        Данная функция принимает в себя обязательный аргумент form_type, за который закрепляется имя формы,
        а так же необязательные позиционные аргументы *args что представляют из себя 
        кнопки, которые необходимо выключить.
        Планируется, что в 
        '''

        if isinstance(spec_forms, str) != True:
            spec_forms = [form_name[1] for form_name in spec_forms] if spec_forms != None else ...
            spec_forms = {form_name:value for form_name in spec_forms for key, value in passed_forms_info.items() if key == form_name} if isinstance(passed_forms_info, dict) == True and spec_forms != None else {form_elem["form_name"]:FORMS.get(form_elem["form_name"]) for form_elem in passed_forms_info}

        public_kb = InlineKeyboardBuilder()
        if len(found_patterns) == 0:
            finish_redirectiong = InlineKeyboardButton(text="Завершить публикацию", callback_data="finish_state")
            
            if file_type == 'message':
                private_chat = InlineKeyboardButton(text="В личные сообщения пользователю", callback_data="private_message")
                section_chat = InlineKeyboardButton(text=f"В раздел формы {spec_forms}", callback_data=f"form_type:{spec_forms}") if isinstance(spec_forms, str) == True else [InlineKeyboardButton(text=f'В раздел формы {form_name}', callback_data=f'form_id:{form_id}&{file_type}') for form_name, form_id in spec_forms.items()]
                open_channel = InlineKeyboardButton(text="В открытый канал", callback_data="open_chat_public")
                public_kb.add(private_chat, section_chat, open_channel, finish_redirectiong) if isinstance(spec_forms, str) == True else public_kb.add(private_chat, *section_chat, open_channel, finish_redirectiong)
            else:
                section_chat = InlineKeyboardButton(text=f"В раздел формы {spec_forms}", callback_data=f"form_type:{spec_forms}&{file_type}") if isinstance(spec_forms, str) == True else [InlineKeyboardButton(text=f'В раздел формы {form_name}', callback_data=f'form_id:{form_id}&{file_type}') for form_name, form_id in spec_forms.items()]
                open_channel = InlineKeyboardButton(text="В открытый канал", callback_data=f"open_chat_public&{file_type}")
                public_kb.add(section_chat, open_channel, finish_redirectiong) if isinstance(spec_forms, str) == True else public_kb.add(*section_chat, open_channel, finish_redirectiong)

            public_kb.adjust(1)
            return public_kb.as_markup()
        else:
            if file_type == 'message':
                BUTTONS_DICT = {
                    'private': InlineKeyboardButton(text="В личные сообщения пользователю", callback_data="private_message"),
                    'form': InlineKeyboardButton(text=f"В раздел формы {spec_forms}", callback_data=f"form_type:{spec_forms}"),
                    'open': InlineKeyboardButton(text="В открытый канал", callback_data="open_chat_public")
                }
            else:
                BUTTONS_DICT = {
                    'form': InlineKeyboardButton(text=f"В раздел формы {spec_forms}", callback_data=f"form_type:{spec_forms}&{file_type}") if isinstance(spec_forms, dict) != True else [InlineKeyboardButton(text=f"В раздел формы {form_name}", callback_data=f"form_type:{form_id}&{file_type}") for form_name, form_id in spec_forms.items()],
                    'open': InlineKeyboardButton(text="В открытый канал", callback_data=f"open_chat_public&{file_type}")
                } 

            found_patterns = set(found_patterns)
            keys = set(BUTTONS_DICT.keys()) 

            resulted_buttons = [BUTTONS_DICT[elem] for elem in keys.difference(found_patterns)] if isinstance(BUTTONS_DICT['form'], list) == True else [BUTTONS_DICT[elem] for elem in keys.difference(found_patterns)]

            if isinstance(resulted_buttons, list):
                try:
                    public_kb.add(*resulted_buttons, InlineKeyboardButton(text="Завершить публикацию", callback_data="finish_state"))
                except ValueError:
                    public_kb.add(*resulted_buttons[0], InlineKeyboardButton(text="Завершить публикацию", callback_data="finish_state"))
            else:
                public_kb.add(*resulted_buttons, InlineKeyboardButton(text="Завершить публикацию", callback_data="finish_state"))
            public_kb.adjust(1)
            return public_kb.as_markup()
        
    def forward_buttons() -> InlineKeyboardMarkup:
        forward_keyboard = InlineKeyboardBuilder()
        
        private = InlineKeyboardButton(text='В личные сообщения пользователю', callback_data='private_public')
        form = InlineKeyboardButton(text='В раздел формы', callback_data='form_public')
        open_chat = InlineKeyboardButton(text='В открытый канал', callback_data='open_chat_public')
        end = InlineKeyboardButton(text='Выйти', callback_data='end_public')

        forward_keyboard.add(private, form, open_chat, end)
        forward_keyboard.adjust(1, repeat=True)
        return forward_keyboard.as_markup()

# -----------------------------------------S-P-E-C-I-A-L-I-S-T-P-A-N-E-L----------------------------------------------
