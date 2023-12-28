# Импортируйте datetime. 
import datetime as dt
# Импортируйте time.
import time

class Quest:
    def __init__(self, name, description, goal, start_time=None, end_time=None):
        self.name = name
        self.description = description
        self.goal = goal
        self.start_time = start_time
        self.end_time = end_time
        # Допишите два свойства класса.
        
    # Напишите методы приема и сдачи квеста.
    def accept_quest(self):
        self.start_time = dt.datetime.now()
        if self.start_time is None:
            return f'Начало "{self.name}" положено.'
        else:
            return 'С этим испытанием вы уже справились.'
        
    def pass_quest(self):
        self.end_time = dt.datetime.now()
        if self.start_time is None:
            return 'Нельзя завершить то, что не имеет начала!'
        else:
            completion_time = self.end_time - self.start_time
            return f'Квест "{self.name}" окончен. Время выполнения квеста:{completion_time}'

quest_name = 'Сбор пиксельники'
quest_goal = 'Соберите 12 ягод пиксельники.'
quest_description = '''
В древнем лесу Кодоборье растёт ягода "пиксельника".
Она нужна для приготовления целебных снадобий.
Соберите 12 ягод пиксельники.'''

new_quest = Quest(quest_name, quest_description, quest_goal) 

print(new_quest.pass_quest())
print(new_quest.accept_quest())
time.sleep(3)
print(new_quest.pass_quest())
print(new_quest.accept_quest())