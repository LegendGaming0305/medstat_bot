from aiogram import Router, F, types
from aiogram.filters import Command

from keyboards import *


router = Router()

@router.message(Command('start'))
async def process_start(message: types.Message) -> None:
    '''
    Выдаем пользователю определенный набор кнопок от его статуса
    '''
    await message.answer('Меню', reply_markup=starting_keyboard.as_markup())