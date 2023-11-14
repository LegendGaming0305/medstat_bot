import asyncpg
from asyncpg.exceptions import DuplicateDatabaseError


class Database():
    def __init__(self):
        self.connection = None
        # self.create_database()
        self.create_connection()
        self.create_table()

    # async def create_database(self) -> None:
    #     '''
    #     Создание БД если ее не существует еще
    #     '''
    #     conn = await asyncpg.connect(database='template1', user='postgres', password='!qwe@123#')
    #     try:
    #         await conn.execute('CREATE DATABASE telegram OWNER postgres')
    #     except DuplicateDatabaseError:
    #         pass
    #     await conn.close()

    async def create_connection(self) -> None:
        '''
        Создание подключения к БД PostrgeSQL
        '''
        self.connection = await asyncpg.connect(database='telegram', user='postgres', password='',
                                                host='localhost')

    async def create_table(self) -> None:
        '''
        Создание таблиц в БД
        '''
        if self.connection is None:
            await self.create_connection()
        await self.connection.execute('''
                            DO $$ BEGIN
                                CREATE TYPE STATE AS ENUM ('Decline', 'Accept', 'Pending');
                                CREATE TYPE LOWER_PRIOR AS ENUM ('USER', 'TESTER', 'OWNER');
                                CREATE TYPE HIGHER_PRIOR AS ENUM ('USER', 'TESTER', 'OWNER', 'ADMIN', 'SPECIALIST');
                                CREATE TYPE CHAT_TYPE AS ENUM ('Personal', 'Group', 'Section');
                            EXCEPTION
                                WHEN duplicate_object THEN null;
                            END $$;''')
        await self.connection.execute('''CREATE TABLE IF NOT EXISTS registration_process(
                                    id SERIAL PRIMARY KEY,
                                    user_id BIGINT CHECK (user_id > 0) NOT NULL, 
                                    subject_name VARCHAR(100),
                                    user_fio VARCHAR(50),
                                    post_name VARCHAR(100),
                                    telephone_number VARCHAR(20),
                                    registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
        await self.connection.execute('''CREATE TABLE IF NOT EXISTS high_priority_users(
                                    id SERIAL PRIMARY KEY,
                                    user_id BIGINT CHECK (user_id > 0) NOT NULL,
                                    user_fio VARCHAR(50),
                                    privilege_type HIGHER_PRIOR NOT NULL,
                                    telegramm_name VARCHAR(50) DEFAULT NULL)''')
        await self.connection.execute('''CREATE TABLE IF NOT EXISTS low_priority_users(
                                    id SERIAL PRIMARY KEY,
                                    user_id BIGINT CHECK (user_id > 0) NOT NULL,
                                    telegramm_name VARCHAR(50),
                                    privilege_type LOWER_PRIOR DEFAULT 'USER',
                                    registration_process_id INTEGER CHECK (registration_process_id > 0) NOT NULL,
                                    FOREIGN KEY (registration_process_id) REFERENCES registration_process (id),
                                    registration_state STATE DEFAULT 'Pending',
                                    process_regulator INTEGER CHECK (process_regulator > 0) DEFAULT NULL,
                                    FOREIGN KEY (process_regulator) REFERENCES high_priority_users (id))''')
        await self.connection.execute('''CREATE TABLE IF NOT EXISTS form_types(
                                      id SERIAL PRIMARY KEY,
                                      form_name VARCHAR(250),
                                      form_tag VARCHAR(10),
                                      specialist SMALLINT CHECK (specialist > 0) DEFAULT NULL,
                                      FOREIGN KEY (specialist) REFERENCES high_priority_users (id))''')
        await self.connection.execute('''CREATE TABLE IF NOT EXISTS questions_forms(
                                      id SERIAL PRIMARY KEY,
                                      lp_user_id INTEGER CHECK (lp_user_id > 0) NOT NULL,
                                      FOREIGN KEY (lp_user_id) REFERENCES low_priority_users (id),
                                      section_form SMALLINT CHECK (section_form > 0) NOT NULL,
                                      FOREIGN KEY (section_form) REFERENCES form_types (id),
                                      question_content TEXT,
                                      question_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                      question_chat_type VARCHAR(20) DEFAULT 'Personal',
                                      question_state STATE DEFAULT 'Pending')''')
        await self.connection.execute('''CREATE TABLE IF NOT EXISTS answer_process(
                                      id SERIAL PRIMARY KEY,
                                      question_id INTEGER CHECK (question_id > 0) NOT NULL,
                                      FOREIGN KEY (question_id) REFERENCES questions_forms (id),
                                      answer_content TEXT,
                                      answer_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                      answer_chat_type VARCHAR(20) DEFAULT 'Personal',
                                      specialist_id BIGINT CHECK (specialist_id > 0) NOT NULL,
                                      FOREIGN KEY (specialist_id) REFERENCES high_priority_users (id))''')
        await self.connection.execute('''CREATE TABLE IF NOT EXISTS miacs (
                                        id SERIAL PRIMARY KEY,
                                        miac_name VARCHAR(100),
                                        miac_adress VARCHAR(250),
                                        telephone_number VARCHAR(25),
                                        email VARCHAR(50) UNIQUE,
                                        site VARCHAR(200),
                                        miac_tag VARCHAR(20))''')
        await self.connection.execute('''CREATE TABLE IF NOT EXISTS regions (
                                        id SERIAL PRIMARY KEY,
                                        region_name VARCHAR(50),
                                        region_tag VARCHAR(20),
                                        miac_id SMALLINT NOT NULL,
                                        FOREIGN KEY (miac_id) REFERENCES miacs (id))''')
        await self.connection.execute('''CREATE TABLE IF NOT EXISTS federal_district (
                                        id SERIAL PRIMARY KEY,
                                        federal_name VARCHAR(45),
                                        district_tag VARCHAR(30))''')
        await self.connection.execute('''CREATE TABLE IF NOT EXISTS federal_district_regions (
                                        federal_district_id INT,
                                        region_id INT,
                                        FOREIGN KEY (federal_district_id) REFERENCES federal_district (id),
                                        FOREIGN KEY (region_id) REFERENCES regions (id),
                                        PRIMARY KEY (federal_district_id, region_id))''')


    async def add_registration_form(self, *args) -> None:
        '''
        Внесение данных пользователя из формы регистрации в registration_process
        :params: 
        subject - субъект МИАЦ
        fio - ФИО сотрудника
        post - должность сотрудника
        telephone_number - номер телефона
        '''
        if self.connection is None:
            await self.create_connection()
        
        test_subj = "Test"

        await self.connection.execute('''INSERT INTO registration_process 
                                           (user_id, subject_name, user_fio, post_name, telephone_number)
                                           VALUES ($1, $2, $3, $4, $5)''', args[0], test_subj, args[1]['fio'], args[1]['post'], args[1]['telephone_number'])

    async def add_higher_users(self) -> None:
        from non_script_files.config import PRIORITY_LIST
        '''
        Внесение данных о пользователей высшего ранга: Moder, Admin, Owner.
        Данные извлекаются из json-файла
        '''

        if self.connection is None:
            await self.create_connection()

        check_higher_users = await self.connection.fetch('''SELECT * FROM high_priority_users''')

        if check_higher_users: 
            pass
        else:
            for level in PRIORITY_LIST.keys():
                row = PRIORITY_LIST[level]
                [await self.connection.execute('''INSERT INTO high_priority_users (user_id, user_fio, privilege_type)
                                                SELECT $1, $2, $3
                                                WHERE NOT EXISTS (
                                                    SELECT 1
                                                    FROM high_priority_users
                                                    WHERE user_id = $1
                                                )''',
                                            row[string_num]["user_id"], row[string_num]["user_fio"], level) for string_num in range(len(row))]
        
    async def after_registration_process(self, *args) -> None:
        '''
        Частичное заполнение данных в low_priority_users с ссылкой на registration_process_id
        из registration_process 
        :params: 
        '''

        if self.connection is None:
            await self.create_connection()

        cursor = await self.connection.fetchrow('''SELECT id, user_fio, registration_date FROM registration_process WHERE user_id = ($1) ORDER BY registration_date DESC LIMIT 1''', args[0])
        user_check = await self.connection.fetchrow('''SELECT * FROM low_priority_users WHERE user_id = ($1)''', args[0])

        if user_check:
            await self.connection.execute('''UPDATE low_priority_users SET registration_process_id = ($1), registration_state = 'Pending' WHERE user_id = ($2)''', cursor[0], args[0])
        else:
            await self.connection.execute('''INSERT INTO low_priority_users (user_id, telegramm_name, registration_process_id) VALUES ($1, $2, $3)''', args[0], args[1], cursor[0])

    async def get_unregistered(self) -> tuple:
        '''
        Извлечение данных о пользователях, со статусом регистрации "Pending"
        '''
        user_reg_forms = []
        if self.connection is None:
            await self.create_connection()
         
        users_rows = await self.connection.fetch("""SELECT registration_process_id FROM low_priority_users WHERE registration_state = 'Pending'""")
        [user_reg_forms.append(await self.connection.fetchrow('''SELECT * FROM registration_process WHERE id = ($1) ORDER BY registration_date DESC LIMIT 1''', elem[0])) for elem in users_rows]

        return users_rows, user_reg_forms 
    
    async def get_massive_of_values(self, form_id: int = None, user_id: int = None) -> tuple:
        '''
            Извлечение всех данных о форме юзера (reg. process) или же о его данных (low_priority) по id формы или по user_id 
        '''
        if self.connection is None:
            await self.create_connection()

        form_info = await self.connection.fetchrow('''SELECT * FROM registration_process WHERE id = ($1)''', form_id) if form_id else await self.connection.fetchrow('''SELECT * FROM registration_process WHERE user_id = ($1)''', user_id)
        user_info = await self.connection.fetchrow('''SELECT * FROM low_priority_users WHERE registration_process_id = ($1)''', form_id) if form_id else await self.connection.fetchrow('''SELECT * FROM low_priority_users WHERE user_id = ($1)''', user_id)

        return form_info, user_info
    
    async def get_lp_user_info(self, lp_user_id: int = None):
        
        if self.connection is None:
            await self.create_connection()
        
        form_id = await self.connection.fetchrow('''SELECT registration_process_id FROM low_priority_users WHERE id = ($1)''', lp_user_id)
        form_information = await self.connection.fetchrow('''SELECT * FROM registration_process WHERE id = ($1)''', form_id[0])
        lp_user_information = await self.connection.fetchrow('''SELECT * FROM low_priority_users WHERE id = ($1)''', lp_user_id)
        
        return form_information, lp_user_information

    async def update_registration_status(self, string_id, admin_id, reg_status) -> None:
        string_id = int(string_id)
        if self.connection is None:
            await self.create_connection()
        inspector_id = await self.connection.fetchrow('''SELECT id FROM high_priority_users WHERE user_id = ($1)''', admin_id)
        inspector_id = inspector_id[0]
        await self.connection.execute('''UPDATE low_priority_users SET registration_state = ($1), process_regulator = ($2) WHERE id = ($3)''', 
                                      reg_status, inspector_id, string_id)
        
    async def get_status(self, user_id: int = None, form_id: int = None) -> str:
        '''
        Получение данных пользователя по его заявке на регистрацию (reg. process) или же по его данным в low_priority таблице
        посредством user_id или form_id 
        '''
        if self.connection is None:
            await self.create_connection()

        return await self.connection.fetchval('''SELECT registration_state FROM low_priority_users WHERE user_id = ($1)''', user_id) if user_id else await self.connection.fetchval('''SELECT registration_process_id FROM low_priority_users WHERE user_id = ($1)''', form_id)

    async def get_lp_user_id(self, user_id: int = None) -> str:

        if self.connection is None:
            await self.create_connection()

        return await self.connection.fetchval('''SELECT id FROM low_priority_users WHERE user_id = ($1)''', user_id)

    async def process_question(self, user_id: int, question: str, form: str) -> None:
        '''
        Ввод вопроса по форме в БД
        '''
        if self.connection is None:
            await self.create_connection()
        form_id = await self.connection.fetchval('''SELECT id FROM form_types WHERE form_tag = $1''', form) 
        await self.connection.execute('''INSERT INTO questions_forms (lp_user_id, section_form, question_content)
                                      VALUES ($1, $2, $3)''', await Database().get_lp_user_id(user_id=user_id), form_id, question)
    
    async def get_specialits_questions(self, specialist_id: int) -> list:
        if self.connection is None:
            await self.create_connection()

        form_id = await self.connection.fetchval('''SELECT ft.id
                                                 FROM form_types ft
                                                 JOIN high_priority_users hp ON ft.specialist = hp.id
                                                 WHERE hp.user_id = $1''', specialist_id)
        result = await self.connection.fetch('''SELECT id, question_content, lp_user_id FROM questions_forms WHERE section_form = $1 AND question_state = 'Pending';''', form_id)
        return result
    
    async def answer_process_report(self, question_id: int, answer: str, specialist_id: int) -> None:
        if self.connection is None:
            await self.create_connection()

        specialist_id = await self.connection.fetchval('''SELECT id FROM high_priority_users WHERE user_id = ($1)''', specialist_id)

        if answer == "Закрытие вопроса":
            await self.connection.execute('''UPDATE questions_forms SET question_state = 'Decline' WHERE id = ($1)''', question_id)
            await self.connection.execute('''INSERT INTO answer_process (question_id, answer_content, specialist_id) VALUES ($1, $2, $3)''', question_id, answer, specialist_id)
        else:
            await self.connection.execute('''UPDATE questions_forms SET question_state = 'Accept' WHERE id = ($1)''', question_id)
            await self.connection.execute('''INSERT INTO answer_process (question_id, answer_content, specialist_id) VALUES ($1, $2, $3)''', question_id, answer, specialist_id)

    async def check_question(self, question_id: int) -> str:
        if self.connection is None:
            await self.create_connection()
        result = await self.connection.fetchval('''SELECT answer_content FROM answer_process WHERE question_id = $1''', question_id)
        return result
    
    async def get_question_form(self, lp_user_id: int):
        if self.connection is None:
            await self.create_connection()
        return await self.connection.fetchrow('''SELECT * FROM questions_forms WHERE lp_user_id = ($1)''', lp_user_id)
    
    async def get_miac_information(self, info_type: str, district_id: int = None, miac_id: int = None):
        '''
        Получение информации для создания inline кнопок
        '''
        if self.connection is None:
            await self.create_connection()
        if info_type == 'federal_district':
            districts = await self.connection.fetch('''SELECT federal_name, district_tag FROM federal_district''')
            return districts
        elif info_type == 'region':
            regions = await self.connection.fetch('''SELECT regions.region_name, regions.region_tag
                                                  FROM regions
                                                  JOIN federal_district_regions ON regions.id = federal_district_regions.region_id
                                                  WHERE federal_district_regions.federal_district_id = $1''', district_id)
            return regions
        elif info_type == 'miac':
            miac = await self.connection.fetchval('''SELECT miac_name FROM miacs
                                                  WHERE id = $1''', miac_id)
            return miac