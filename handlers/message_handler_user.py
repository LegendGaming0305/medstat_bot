from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext

from states import User_states, Admin_states
from main import db
from keyboards import *

router = Router()

@router.message(User_states.registration)
async def process_subject_input(message: types.Message, state: FSMContext) -> None:
    '''
    Получение наименования субъекта МИАЦ
    '''
    await state.update_data(subject=message.text)
    await message.answer('Введите Ваше ФИО строго через пробел')
    await state.set_state(User_states.reg_fio)

@router.message(User_states.reg_fio)
async def process_fio_input(message: types.Message, state: FSMContext) -> None:
    '''
    Получение ФИО
    '''
    await state.update_data(fio=message.text)
    await message.answer('Введите Вашу должность')
    await state.set_state(User_states.reg_post)

@router.message(User_states.reg_post)
async def process_post_input(message: types.Message, state: FSMContext) -> None:
    '''
    Получение наименования должности
    '''
    await state.update_data(post=message.text)
    await message.answer('Укажите Ваш номер телефона в формате +7 (999) 999-99-99')
    await state.set_state(User_states.reg_telephone_number)

@router.message(User_states.reg_telephone_number)
async def process_telephone_number_input(message: types.Message, state: FSMContext) -> None:
    '''
    Получение номера телефона
    '''
    await state.update_data(telephone_number=message.text)
    await message.answer('''Ваши данные отправлены на проверку, ожидайте подтверждения.
После чего Вы сможете задать вопрос специалисту''', reply_markup=starting_keyboard.as_markup())
    data = await state.get_data()
    await db.add_registration_form(message.from_user.id, data)
    await db.after_registration_process(message.from_user.id, message.from_user.full_name)
    await state.set_state(Admin_states.registration_claim)