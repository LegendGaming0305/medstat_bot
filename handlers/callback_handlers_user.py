from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext

from states import User_states
from additional_functions import access_block_decorator
from handlers.callback_handlers_admin import admin_cb_router

user_cb_router = Router()
user_cb_router.include_router(admin_cb_router)

@user_cb_router.callback_query()
async def process_starting_callbacks(callback: types.CallbackQuery, state: FSMContext) -> None:
    '''
    Обработка запросов от inline-кнопок user-a
    '''
    @access_block_decorator
    async def registration_start(callback: types.CallbackQuery, state: FSMContext):
        await state.set_state(User_states.registration)
        await callback.message.edit_text('Введите наименование вашего МИАЦ')

    if callback.data == 'npa':
        await callback.message.edit_text('НПА')
    elif callback.data == 'medstat':
        await callback.message.edit_text('Медстат')
    elif callback.data == 'statistic':
        await callback.message.edit_text('Статистика')
    elif callback.data == 'method_recommendations':
        await callback.message.edit_text('Методические рекомендации')
    elif callback.data == 'registration':
        await registration_start(callback, state)