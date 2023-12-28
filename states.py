from aiogram.fsm.state import State, StatesGroup

class User_states(StatesGroup):
    registration = State()
    reg_organisation = State()
    reg_post = State()
    registration_accepted = State()
    form_choosing = State()
    question_process = State()
    fuzzy_process = State()
    file_date = State()

class Admin_states(StatesGroup):
    registration_process = State()
    post_publication = State()
    file_loading = State()
    delete_member = State()
    
class Specialist_states(StatesGroup):
    choosing_question = State()
    answer_question = State()
    public_choose_message = State()
    public_choose_file = State()

