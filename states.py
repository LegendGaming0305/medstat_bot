from aiogram.fsm.state import State, StatesGroup

class User_states(StatesGroup):
    registration = State()
    reg_fio = State()
    reg_post = State()
    reg_telephone_number = State()
    registration_accepted = State()
    form_choosing = State()
    question_process = State()

class Admin_states(StatesGroup):
    registration_claim = State()
    registration_process = State()