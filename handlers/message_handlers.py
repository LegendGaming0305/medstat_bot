from additional_functions import user_registration_decorator
from states import User_states, Admin_states, Specialist_states
from main import db
from keyboards import User_Keyboards, Specialist_keyboards
from cache_container import cache

from aiogram.fsm.context import FSMContext
from aiogram import Router, F, types
from aiogram.filters import Command
import json

router = Router()

@router.message(Command('start'))
@user_registration_decorator
async def process_start(message: types.Message, state: FSMContext) -> None:
    '''
    Выдаем пользователю определенный набор кнопок от его статуса
    '''
    await state.clear()

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
После чего Вы сможете задать вопрос специалисту''', reply_markup=User_Keyboards.main_menu(True).as_markup())
    await db.add_registration_form(message.from_user.id, await state.get_data())
    await db.after_registration_process(message.from_user.id, message.from_user.full_name)
    await state.clear()

@router.message(User_states.question_process)
async def process_question_input(message: types.Message, state: FSMContext) -> None:
    '''
    Передача вопроса в бд
    '''
    data = await state.get_data()
    await db.process_question(user_id=message.from_user.id, question=message.text, form=data['tag'])
    await message.answer('Ваш вопрос передан', reply_markup=User_Keyboards.main_menu(True).as_markup())
    await state.clear()

@router.message(Specialist_states.answer_question)
async def process_answer(message: types.Message, state: FSMContext):
    from main import bot
    data = await state.get_data()
    question_id = data['question_id']
    user_id = data['user_id']
    await db.update_question(question_id=int(question_id),
                             answer=message.text,
                             specialist_id=message.from_user.id)
    await bot.send_message(chat_id=user_id, text=f'Ответ:\n{message.text}')
    await message.reply('Ответ отправлен', reply_markup=Specialist_keyboards.questions_gen())
    await state.clear()