import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from handlers import message_handlers_general, callback_handlers_user, message_handler_user
from db_actions import Database

dp = Dispatcher(storage=MemoryStorage())
db = Database()

async def on_startup():
    await db.create_database()
    await db.create_connection()
    await db.create_table()
    print('Бот запущен!')

async def on_shutdown():
    print('Бот выключен!')

async def main() -> None:
    from config import API_TELEGRAM
    bot = Bot(API_TELEGRAM, parse_mode=ParseMode.HTML)
    await bot.delete_webhook(drop_pending_updates=True)
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    dp.include_routers(message_handlers_general.router, callback_handlers_user.router, message_handler_user.router)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())