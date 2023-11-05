import asyncpg

class Database:
    def __init__(self):
        self.connection = None
        self.create_table()
        self.create_connection()

async def create_connection(self):
        # Создание соединения с базой данных
        self.connection = await asyncpg.create_pool()