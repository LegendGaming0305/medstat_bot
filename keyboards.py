from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton

starting_keyboard = InlineKeyboardBuilder()

# ----------------------------------------------U-S-E-R-T-P-A-N-E-L----------------------------------------------
npa_button = InlineKeyboardButton(text='НПА', callback_data='npa')
medstat_button = InlineKeyboardButton(text='Медстат', callback_data='medstat')
statistic_button = InlineKeyboardButton(text='Статистика', callback_data='statistic')
method_recommendations_button = InlineKeyboardButton(text='Методические рекомендации', callback_data='method_recommendations')
registration_button = InlineKeyboardButton(text='Регистрация', callback_data='registration')
make_question_button = InlineKeyboardButton(text='Задать вопрос', callback_data='make_question')
# ----------------------------------------------U-S-E-R-T-P-A-N-E-L----------------------------------------------

starting_keyboard.add(npa_button, 
                      medstat_button, 
                      statistic_button, 
                      method_recommendations_button, 
                      registration_button)

starting_keyboard.adjust(1, repeat=True)