from aiogram.fsm.state import State, StatesGroup

class User_states(StatesGroup):
    registration = State()
    reg_organisation = State()
    reg_post = State()
    registration_accepted = State()
    form_choosing = State()
    question_process = State()
    fuzzy_process = State()

class Admin_states(StatesGroup):
    registration_claim = State()
    registration_process = State()
    
class Specialist_states(StatesGroup):
    choosing_question = State()
    answer_question = State()
    choosing_publication_destination = State()
    public_choose = State()
