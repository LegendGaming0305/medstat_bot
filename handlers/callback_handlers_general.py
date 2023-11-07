from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext

router = Router()

@router.callback_query()
async def process_starting_callbacks(callback: types.CallbackQuery, state: FSMContext) -> None:
    '''
    Обработка запросов от inline-кнопок
    '''

    if callback.data == 'menu':
        pass