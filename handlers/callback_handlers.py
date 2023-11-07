from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.enums import ParseMode

from keyboards import Admin_Keyboards
from db_actions import Database
from states import Admin_states
from states import User_states
from additional_functions import access_block_decorator


db = Database()
router = Router()

@router.callback_query(Admin_states.registration_process)
async def process_starting_admin(callback: types.CallbackQuery, state: FSMContext) -> None:
    from aiogram import Bot
    from non_script_files.config import API_TELEGRAM
    '''
    Обработка запросов от inline-кнопок admin-a
    '''
    callback_data = callback.data
    unreg_data = await db.get_unregistered()

    if callback_data == 'check_reg':
        await callback.message.edit_text(text="Выберете заявку из предложенных:", reply_markup=Admin_Keyboards.application_gen(unreg_data))
    elif 'dec_app' in callback_data:
        callback_data = callback_data.split(":")
        await Bot(API_TELEGRAM, parse_mode=ParseMode.HTML).send_message(chat_id = int(callback_data[1]), text="Ваша заявка была отклонена", reply_markup=Admin_Keyboards.application_gen(unreg_data))
    elif 'acc_app' in callback_data:
        callback_data = callback_data.split(":")
        await Bot(API_TELEGRAM, parse_mode=ParseMode.HTML).send_message(chat_id = int(callback_data[1]), text="Ваша заявка была подтверждена", reply_markup=Admin_Keyboards.application_gen(unreg_data))
    elif "generated" in callback_data:
        cb_data = callback.data ; cb_data = cb_data.split("&") ; cb_data = cb_data[1].split(":")
    
        callback_id = int(cb_data[1])
        info_list = await db.get_certain_form(callback_id)
        information_panel = f"""Название субъекта: {info_list[2]},\nФИО: {info_list[3]},\nДолжность: {info_list[4]},\nНомер телефона: {info_list[5]}"""
        await callback.message.edit_text(text=information_panel, reply_markup=Admin_Keyboards.reg_process_keyboard(info_list[1]))

# @router.callback_query(Admin_states.registration_claim, lambda callback: "generated" in callback)
# async def admin_gen_button_processing(callback: types.CallbackQuery, state: FSMContext) -> None:
#     '''
#         Обработка callback-а от сгенерированной кнопки
#     '''
#     callback = callback.data ; callback = callback.split("&") ; callback = callback[1].split(":")
    
#     callback_id = int(callback[1])
#     info_list = db.get_certain_form(callback_id)
#     information_panel = f"""
#         Название субъекта: {info_list[2]},\n
#         ФИО: {info_list[3]},\n
#         Должность: {info_list[4]},\n
#         Номер телефона: {info_list[5]}"""
#     callback.message.edit_text(text=information_panel, reply_markup=Admin_Keyboards.reg_process_keyboard(info_list[1]))

@router.callback_query()
async def process_starting_user(callback: types.CallbackQuery, state: FSMContext) -> None:
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
    elif callback.data == 'admin_panel':
        await callback.message.edit_text(text="Добро пожаловать в Админ-панель", reply_markup=Admin_Keyboards.main_menu())
        await state.set_state(Admin_states.registration_process)
    elif callback.data == 'tester_panel':
        pass
    elif callback.data == 'moder_panel':
        pass
    elif callback.data == 'user_panel':
        pass

@router.callback_query()
async def process_starting_general(callback: types.CallbackQuery, state: FSMContext) -> None:
    '''
    Обработка запросов от inline-кнопок
    '''

    if callback.data == 'menu':
        pass