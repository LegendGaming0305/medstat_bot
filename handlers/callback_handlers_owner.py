from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext

from keyboards import *

owner_cb_router = Router()

@owner_cb_router.callback_query()
async def process_starting_callbacks(callback: types.CallbackQuery, state: FSMContext) -> None:
    '''
    Обработка запросов от inline-кнопок owner-a
    '''
    if callback.data == 'admin_panel':
        callback.message.edit_text(text="Добро пожаловать в Админ-панелью", reply_markup=Admin_Keyboards.admin_starting_keyboard)
    elif callback.data == 'tester_panel':
        pass
    elif callback.data == 'moder_panel':
        pass
    elif callback.data == 'user_panel':
        pass
    