from aiogram import Router, F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from additional_functions import user_registration_decorator
from handlers.message_handlers_user import user_ms_router

general_ms_router = Router()
general_ms_router.include_router(user_ms_router)

@general_ms_router.message(Command('start'))
@user_registration_decorator
async def process_start(message: types.Message, state: FSMContext) -> None:
    '''
    Выдаем пользователю определенный набор кнопок от его статуса
    '''
    pass


    
