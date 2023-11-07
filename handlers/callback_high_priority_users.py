from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from main import Global_Data_Storage

from keyboards import Admin_Keyboards
from db_actions import Database
from states import Admin_states

db = Database()
highlvl_cb_router = Router()

@highlvl_cb_router.callback_query()
async def process_starting_admin(callback: types.CallbackQuery, state: FSMContext) -> None:
    '''
    Обработка запросов от inline-кнопок admin-a
    '''
    callback_data = callback.data
    unreg_data = await db.get_unregistered()

    if callback_data == 'check_reg':
        await Global_Data_Storage.bot_specimen.send_message(chat_id = callback.from_user.id, text="Выберете заявку из предложенных:", reply_markup=Admin_Keyboards.application_gen(unreg_data))
    elif 'dec_app' in callback_data:
        callback_data = callback_data.split(":")
        await Global_Data_Storage.bot_specimen.send_message(chat_id = int(callback_data[1]), text="Ваша заявка была отклонена", reply_markup=Admin_Keyboards.application_gen(unreg_data))
    elif 'acc_app' in callback_data:
        callback_data = callback_data.split(":")
        await Global_Data_Storage.bot_specimen.send_message(chat_id = int(callback_data[1]), text="Ваша заявка была подтверждена", reply_markup=Admin_Keyboards.application_gen(unreg_data))

@highlvl_cb_router.callback_query(Admin_states.registration_claim, lambda callback: "generated" in callback)
async def gen_button_processing(callback: types.CallbackQuery, state: FSMContext) -> None:
    '''
        Обработка callback-а от сгенерированной кнопки
    '''
    callback = callback.data ; callback = callback.split("&") ; callback = callback[1].split(":")
    
    callback_id = int(callback[1])
    info_list = db.get_certain_form(callback_id)
    information_panel = f"""
        Название субъекта: {info_list[2]},\n
        ФИО: {info_list[3]},\n
        Должность: {info_list[4]},\n
        Номер телефона: {info_list[5]}"""
    callback.message.edit_text(text=information_panel, reply_markup=Admin_Keyboards.reg_process_keyboard(info_list[1]))

@highlvl_cb_router.callback_query()
async def process_starting_owner(callback: types.CallbackQuery, state: FSMContext) -> None:
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
    

