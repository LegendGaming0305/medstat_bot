import asyncpg
from asyncpg.exceptions import DuplicateDatabaseError

from non_script_files import config

class Database():
    def __init__(self):
        self.connection = None
        self.create_database()
        self.create_connection()
        self.create_table()

    async def create_database(self) -> None:
        '''
        Создание БД если ее не существует еще
        '''
        conn = await asyncpg.connect(database='template1', user='postgres')
        try:
            await conn.execute('CREATE DATABASE telegram OWNER postgres')
        except DuplicateDatabaseError:
            pass
        await conn.close()

    async def create_connection(self) -> None:
        '''
        Создание подключения к БД PostrgeSQL
        '''
        self.connection = await asyncpg.connect('postgresql://postgres@localhost/telegram')

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
                                CREATE TYPE HIGHER_PRIOR AS ENUM ('USER', 'TESTER', 'OWNER', 'ADMIN');
                            EXCEPTION
                                WHEN duplicate_object THEN null;
                            END $$;''')
        await self.connection.execute('''CREATE TABLE IF NOT EXISTS registration_process(
                                    id SERIAL PRIMARY KEY,
                                    user_id BIGINT CHECK (user_id > 0) NOT NULL, 
                                    subject_name VARCHAR(100),
                                    user_fio VARCHAR(50),
                                    post_name VARCHAR(100),
                                    telephone_number VARCHAR(12),
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
                                    process_regulator INTEGER CHECK (process_regulator > 0) NOT NULL,
                                    FOREIGN KEY (process_regulator) REFERENCES high_priority_users (id))''')
        await self.connection.close()

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
        
        await self.connection.execute('''INSERT INTO registration_process 
                                           (user_id, subject_name, user_fio, post_name, telephone_number)
                                           VALUES ($1, $2, $3, $4, $5)''', args[0], args[1]['subject'], args[1]['fio'], args[1]['post'], args[1]['telephone_number'])
        await self.connection.close()

    async def add_higher_users(self) -> None:
        if self.connection is None:
            await self.create_connection()

        for level in config.PRIORITY_LIST.keys():
            row = config.PRIORITY_LIST[level]
            [await self.connection.execute('''INSERT INTO high_priority_users (user_id, user_fio, privilege_type) VALUES ($1, $2, $3)''',
                                          row[string_num]["user_id"], row[string_num]["user_fio"], level) for string_num in range(len(row))]
        await self.connection.close()

    async def after_registration_process(self, args) -> None:
        '''
        Частичное заполнение данных в low_priority_users с ссылкой на registration_process_id
        :params: 
        
        '''

        if self.connection is None:
            await self.create_connection()

        async with self.connection.execute('''SELECT id, user_fio, registration_date FROM registration_process ORDER BY registration_date DESC LIMIT 3''') as exported_information:
            data_rows = await exported_information.fetchall()
            await self.connection.execute('''INSERT INTO low_priority_users (user_id, telegramm_name) VALUES ($1, $2)''', args[0], args[1])
            await self.connection.execute('''UPDATE low_priority_users SET registration_process_id = ($1)''', )
