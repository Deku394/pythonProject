#вёрстка клавиатур
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

start_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Консультация", callback_data="consultation")],
    [InlineKeyboardButton(text="Бесплатные курсы", callback_data="free_courses")],
    [InlineKeyboardButton(text="Массфолл для блога", url='https://t.me/ZackFosteroverkill')],
    [InlineKeyboardButton(text="Мой канал в тг", url='https://t.me/rudnyov')],
    [InlineKeyboardButton(text="Про продвижение", callback_data="about_instagram")],
]
)

consultation_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Назад в главное меню', callback_data='back_menu')],
    ]
)

free_courses_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Курс по хэштегам', url='https://t.me/rudnyov')],
        [InlineKeyboardButton(text='Система вечного контента', url='https://t.me/rudnyov')],
        [InlineKeyboardButton(text='Обучение по отметкам', url='https://t.me/rudnyov')],
        [InlineKeyboardButton(text='Назад в главное меню', callback_data='back_menu')]
    ]
)

about_instagram_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Рабочая тетрадь по сторис', callback_data='story_notebook')],
        [InlineKeyboardButton(text='Марафон по продвижению', callback_data='inst_marathon')],
        [InlineKeyboardButton(text='Канал "штучки для рилс"', url='https://t.me/rudnyov')],
        [InlineKeyboardButton(text='Задать вопрос', callback_data='ask_question')],
        [InlineKeyboardButton(text='Назад в главное меню', callback_data='back_menu')],
    ]
)

story_notebook_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Назад', callback_data='back_list')],
        [InlineKeyboardButton(text='Назад в главное меню', callback_data='back_menu')],
    ]
)

instagram_marathon_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Присоединиться', url='https://t.me/rudnyov')],
        [InlineKeyboardButton(text='Назад', callback_data='back_list')],
        [InlineKeyboardButton(text='Назад в главное меню', callback_data='back_menu')]
    ]
)

ask_question_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Назад', callback_data='back_list')],
        [InlineKeyboardButton(text='Назад в главное меню', callback_data='back_menu')],
    ]
)
