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
        await self.connection.execute('''CREATE TABLE IF NOT EXISTS registration_form(
                            id SERIAL PRIMARY KEY,
                            user_id INTEGER,
                            subject_name TEXT,
                            user_fio TEXT,
                            post TEXT,
                            telephone_number TEXT,
                            privilege_id INTEGER
        )''')
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
