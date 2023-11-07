from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext

from handlers.callback_handlers_user import user_cb_router

general_cb_router = Router()
general_cb_router.include_router(user_cb_router)

@general_cb_router.callback_query()
async def process_starting_callbacks(callback: types.CallbackQuery, state: FSMContext) -> None:
    '''
    Обработка запросов от inline-кнопок
    '''

    if callback.data == 'menu':
        pass