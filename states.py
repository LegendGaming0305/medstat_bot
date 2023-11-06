from aiogram.fsm.state import State, StatesGroup

class User_states(StatesGroup):
    registration = State()
    reg_fio = State()
    reg_post = State()
    reg_telephone_number = State()