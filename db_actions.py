import asyncpg

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
        conn = await asyncpg.connect(database='template1',
                                     user='postgres')
        await conn.execute('CREATE DATABASE telegram OWNER postgres')
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
        await self.connection.execute('''CREATE TABLE IF NOT EXISTS registration_process(
                            id SERIAL PRIMARY KEY,
                            subject_name VARCHAR(100),
                            user_fio VARCHAR(50),
                            post_name VARCHAR(100),
                            telephone_number VARCHAR(12),
                            registration_date DATETIME DEFAULT CURRENT_TIMESTAMP)''')
        await self.connection.execute('''CREATE TABLE IF NOT EXISTS high_priority_users(
                            id SERIAL PRIMARY KEY,
                            user_id INTEGER UNSIGNED NOT NULL,
                            privilege_type ENUM("USER", "TESTER", "OWNER", "ADMIN"),
                            telegramm_name VARCHAR(50))''')
        await self.connection.execute(
            '''CREATE TABLE IF NOT EXISTS low_priority_users(
                id SERIAL PRIMARY KEY,
                user_id INTEGER UNSIGNED NOT NULL,
                telegramm_name VARCHAR(50),
                privilege_type ENUM("USER", "TESTER", "OWNER") DEFAULT "USER",
                registration_process_id INTEGER UNSIGNED NOT NULL,
                FOREIGN KEY (registration_process_id) REFERENCES registration_process (id),
                registration_state ENUM("Decline", "Accept", "Pending"),
                process_regulator INTEGER UNSIGNED NOT NULL,
                FOREIGN KEY (process_regulator) REFERENCES high_priority_users (id)''')
        await self.connection.close()

    async def add_registration_form(self, *args) -> None:
        '''
        Внесение данных их формы регистрации
        :params: 
        subject - субъект МИАЦ
        fio - ФИО сотрудника
        post - должность сотрудника
        telephone_number - номер телефона
        '''
        if self.connection is None:
            await self.create_connection()
        
        await self.connection.execute('''INSERT INTO registration_form 
                                           (user_id, subject_name, fio, post, telephone_number)
                                           VALUES ($1, $2, $3, $4, $5)''', args[0],
                                                                       args[1]['subject'],
                                                                       args[1]['fio'],
                                                                       args[1]['post'],
                                                                       args[1]['telephone_number'])
        await self.connection.close()
