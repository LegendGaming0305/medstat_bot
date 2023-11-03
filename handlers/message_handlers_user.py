from aiogram import Router, F, types
from aiogram.filters import Command


router = Router()

@router.message(Command('start'))
async def process_start(message: types.Message):
    await message.answer('Привет')