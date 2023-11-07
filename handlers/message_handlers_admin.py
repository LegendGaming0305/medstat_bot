from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext

from handlers.message_handlers_owner import owner_ms_router

admin_ms_router = Router()
admin_ms_router.include_router(owner_ms_router)