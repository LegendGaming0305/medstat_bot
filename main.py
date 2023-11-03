import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode

from config import API_TELEGRAM
from handlers import message_handlers_user

dp = Dispatcher()

async def on_startup():
    print('Бот запущен!')

async def on_shutdown():
    print('Бот выключен!')

async def main() -> None:
    bot = Bot(API_TELEGRAM, parse_mode=ParseMode.HTML)
    await bot.delete_webhook(drop_pending_updates=True)
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    dp.include_routers(message_handlers_user.router)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())