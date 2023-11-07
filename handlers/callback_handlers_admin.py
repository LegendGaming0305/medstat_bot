from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext

from handlers.callback_handlers_owner import owner_cb_router

admin_cb_router = Router()
admin_cb_router.include_router(owner_cb_router)

@admin_cb_router.callback_query()
async def process_starting_callbacks(callback: types.CallbackQuery, state: FSMContext) -> None:
    '''
    Обработка запросов от inline-кнопок admin-a
    '''

    if callback.data == 'admin_panel':
        pass
    