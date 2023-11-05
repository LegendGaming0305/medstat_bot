from aiogram.fsm.state import State, StatesGroup

class User_states(StatesGroup):
    registration = State()
    fio = State()
    post = State()
    telephone_number = State()