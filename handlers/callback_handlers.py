from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.enums import ParseMode

from keyboards import Admin_Keyboards, User_Keyboards
from db_actions import Database
from states import Admin_states
from states import User_states

db = Database()
router = Router()

@router.callback_query(User_states.form_choosing)
async def process_starting_general(callback: types.CallbackQuery, state: FSMContext) -> None:
    '''
    Обработка запросов от inline-кнопок форм
    '''
    await state.set_state(User_states.question_process)
    await state.update_data(tag=callback.data)
    await callback.message.edit_text('Введите Ваш вопрос.')

@router.callback_query(Admin_states.registration_process)
async def process_admin(callback: types.CallbackQuery, state: FSMContext) -> None:
    from aiogram import Bot
    from non_script_files.config import API_TELEGRAM
    '''
    Обработка запросов от inline-кнопок admin-a
    '''
    callback_data = callback.data
    unreg_data = await db.get_unregistered()

    if callback_data == 'check_reg':
        await callback.message.edit_text(text="Выберете заявку из предложенных:", reply_markup=Admin_Keyboards.application_gen(unreg_data).as_markup())
    elif 'dec_app' in callback_data:
        callback_data = callback_data.split(":")
        await Bot(API_TELEGRAM, parse_mode=ParseMode.HTML).send_message(chat_id = int(callback_data[1]), text="Ваша заявка была отклонена")
        await db.update_registration_status(string_id=callback_data[2],
                                            admin_id=callback.from_user.id,
                                            reg_status="Decline")
        await callback.message.edit_text('Меню', reply_markup=Admin_Keyboards.main_menu())
        await state.clear()
    elif 'acc_app' in callback_data:
        callback_data = callback_data.split(":")
        await Bot(API_TELEGRAM, parse_mode=ParseMode.HTML).send_message(chat_id = int(callback_data[1]), text="Ваша заявка была подтверждена")
        await db.update_registration_status(string_id=callback_data[2],
                                            admin_id=callback.from_user.id,
                                            reg_status="Accept")
        await callback.message.edit_text('Меню', reply_markup=Admin_Keyboards.main_menu())
        await state.clear()
    elif "generated" in callback_data:
        cb_data = callback.data ; cb_data = cb_data.split("&") ; cb_data = cb_data[1].split(":") ; callback_id = int(cb_data[1])
        info_tuple = await db.get_massive_of_values(user_id=callback_id)
        form_info_list, user_info_list = info_tuple[0], info_tuple[1]
        information_panel = f"""Название субъекта: {form_info_list[2]},\nФИО: {form_info_list[3]},\nДолжность: {form_info_list[4]},\nНомер телефона: {form_info_list[5]}"""
        await callback.message.edit_text(text=information_panel, reply_markup=Admin_Keyboards.reg_process_keyboard(form_info_list[1], user_info_list[0]).as_markup())

@router.callback_query()
async def process_user(callback: types.CallbackQuery, state: FSMContext) -> None:
    '''
    Обработка запросов от inline-кнопок user-a
    '''

    if callback.data == 'npa':
        await callback.message.edit_text('НПА')
    elif callback.data == 'medstat':
        await callback.message.edit_text('Медстат')
    elif callback.data == 'statistic':
        await callback.message.edit_text('Статистика')
    elif callback.data == 'method_recommendations':
        await callback.message.edit_text('Методические рекомендации')
    elif callback.data == 'registration':
        await state.set_state(User_states.registration)
        await callback.message.edit_text('Введите наименование вашего МИАЦ')
    elif callback.data == "make_question":
        status = await db.get_certain_value(data_to_find="privilege_type", user_id=callback.from_user.id)
        match status:
            case 'Accept':
                await callback.message.edit_text(text='Выберите раздел', reply_markup=User_Keyboards.section_chose().as_markup())
                await state.set_state(User_states.form_choosing)
            case 'Pending':
                await callback.message.edit_text(text='Ваша заявка на рассмотрении и пока что у Вас нет доступа к этому разделу',
                                             reply_markup=User_Keyboards.main_menu(True))
            case 'Decline':
                await callback.message.edit_text(text='Ваша заявка отклонена и пока что у Вас нет доступа к этому разделу',
                                             reply_markup=User_Keyboards.main_menu(False))
    elif callback.data == 'admin_panel':
        await callback.message.edit_text(text="Добро пожаловать в Админ-панель", reply_markup=Admin_Keyboards.main_menu())
        await state.set_state(Admin_states.registration_process)
    elif callback.data == 'tester_panel':
        pass
    elif callback.data == 'moder_panel':
        pass
    elif callback.data == 'user_panel':
        pass
