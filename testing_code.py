from sqlalchemy import URL, create_engine, MetaData, select, and_
from sqlalchemy.orm import Session

# url_object = URL.create(
#     drivername='postgresql+psycopg2',
#     username='postgres',
#     password='!qwe@123#',
#     host='localhost',
#     database='telegram'
# )

# engine = create_engine(url=url_object)

# metadata = MetaData()
# metadata.reflect(bind=engine)

# high_priority_users = metadata.tables['high_priority_users']
# questions_forms = metadata.tables['questions_forms']
# form_types = metadata.tables['form_types']
# specialist_forms = metadata.tables['specialist_forms']
# low_priority_users = metadata.tables['low_priority_users']
# registration_process = metadata.tables['registration_process']
# answer_process = metadata.tables['answer_process']

# with Session(autoflush=False, bind=engine) as session:
#     people = session.execute(
#         select(questions_forms.c.id,
#                questions_forms.c.question_content,
#                questions_forms.c.lp_user_id,
#                form_types.c.form_name,
#                questions_forms.c.question_message,
#                registration_process.c.subject_name,
#                answer_process.c.answer_content)
#         .join(form_types, questions_forms.c.section_form == form_types.c.id)
#         .join(specialist_forms, form_types.c.id == specialist_forms.c.form_id)
#         .join(high_priority_users, specialist_forms.c.specialist_id == high_priority_users.c.id)
#         .join(low_priority_users, questions_forms.c.lp_user_id == low_priority_users.c.id)
#         .join(registration_process, low_priority_users.c.registration_process_id == registration_process.c.id)
#         .join(answer_process, questions_forms.c.id == answer_process.c.question_id, full=True)
#         .where(
#             and_(high_priority_users.c.user_id == 869012176,
#                  registration_process.c.subject_name == 'Ростовская область',
#                  questions_forms.c.question_state.in_(['Accept', 'Pending']),
#                  form_types.c.form_tag == 'sec_two'))
#         ).all()
    # print(people)

class SearchFilter:
    '''
    Класс для фильтрации вывода вопросов
    '''
    def __init__(self, specialist_id: int) -> None:
        self.specialist_id = specialist_id
        self.region = None
        self.form = None
        self.question_states = []
        self.filter_args = dict()
        self.metadata = None

    async def fetch_questions(self) -> list:
        '''
        Получение данных из бд с применением фильтров и возврат списка вопросов
        '''
        self.database_connection()
        result = self.construct_query()
        return result

    def database_connection(self) -> None:
        url_object = URL.create(
            drivername='postgresql+psycopg2',
            username='postgres',
            password='!qwe@123#',
            host='localhost',
            database='telegram'
        )

        self.engine = create_engine(url=url_object)

        metadata = MetaData()
        metadata.reflect(bind=self.engine)
        self.metadata = metadata
        
    def construct_query(self) -> None:
        with Session(autoflush=False, bind=self.engine) as session:
            self.high_priority_users = self.metadata.tables['high_priority_users']
            self.questions_forms = self.metadata.tables['questions_forms']
            self.form_types = self.metadata.tables['form_types']
            self.specialist_forms = self.metadata.tables['specialist_forms']
            self.low_priority_users = self.metadata.tables['low_priority_users']
            self.registration_process = self.metadata.tables['registration_process']
            self.answer_process = self.metadata.tables['answer_process']

            if self.region:
                self.add_region_filter()

            if self.question_states:
                self.add_question_states_filter()
            else:
                self.question_states.append('Pending')
                self.add_question_states_filter()
                
            if self.form:
                self.add_form()

            result = session.execute(
                select(self.questions_forms.c.id,
                    self.questions_forms.c.question_content,
                    self.questions_forms.c.lp_user_id,
                    self.form_types.c.form_name,
                    self.questions_forms.c.question_message,
                    self.registration_process.c.subject_name,
                    self.answer_process.c.answer_content)
                .join(self.form_types, self.questions_forms.c.section_form == self.form_types.c.id)
                .join(self.specialist_forms, self.form_types.c.id == self.specialist_forms.c.form_id)
                .join(self.high_priority_users, self.specialist_forms.c.specialist_id == self.high_priority_users.c.id)
                .join(self.low_priority_users, self.questions_forms.c.lp_user_id == self.low_priority_users.c.id)
                .join(self.registration_process, self.low_priority_users.c.registration_process_id == self.registration_process.c.id)
                .join(self.answer_process, self.questions_forms.c.id == self.answer_process.c.question_id, full=True)
                .where(
                    and_(self.high_priority_users.c.user_id == self.specialist_id, *self.filter_args.items))
                ).all()
            
            return result

    def add_region_filter(self) -> None:
        self.filter_args['subject'] = self.registration_process.c.subject_name == self.region    

    def add_question_states_filter(self) -> None:
        self.filter_args['states'] = self.questions_forms.c.question_state.in_(self.question_states)

    def add_form(self) -> None:
        self.filter_args['form'] = self.form_types.c.form_tag == self.form

test = SearchFilter(specialist_id=869012176)
test.region = 'Ростовская область'
# test.question_states.append('Accept')
# test.question_states.append('Pending')
# test.form = 'sec_two'
print(test.fetch_questions()[0]._mapping)