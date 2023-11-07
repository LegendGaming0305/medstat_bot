import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
import asyncio as asy
from asyncpg.exceptions._base import InterfaceError

from handlers import message_handlers_general, callback_handlers_general
from non_script_files import config 
from db_actions import Database

class Global_Data_Storage():
    bot_specimen = ''

dp = Dispatcher(storage=MemoryStorage())
db = Database()

async def on_startup():
    await db.create_database()
    await db.create_connection()
    await db.create_table()
    await db.add_higher_users()
    print('Бот запущен!')

async def on_shutdown():
    print('Бот выключен!')

async def main() -> None:
    bot = Bot(config.API_TELEGRAM, parse_mode=ParseMode.HTML)
    Global_Data_Storage.bot_specimen = bot
    await bot.delete_webhook(drop_pending_updates=True)
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    dp.include_routers(message_handlers_general.general_ms_router,  
                       callback_handlers_general.general_cb_router)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())