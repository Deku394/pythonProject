#вёрстка клавиатур
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

start_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Начать", callback_data="begin")],
]
)

begin_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Смотреть урок", callback_data="watch_lesson")],
    [InlineKeyboardButton(text='Назад', callback_data='back_list_1')],
]
)

watch_lesson_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Посмотреть урок №1", url='https://rutube.ru/video/private/fce9ff4430c633f3b240b7a4217819b8/?p=rbtXhxZ3ZiQZsNvQGXLLMg')],
    [InlineKeyboardButton(text="Перейти к следующему блоку", callback_data="next_block_1")],
    [InlineKeyboardButton(text='Назад', callback_data='back_list_2')],
]
)

next_block_1_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Смотреть урок №2", callback_data="watch_lesson_2")],
    [InlineKeyboardButton(text='Назад', callback_data='back_list_3')],
]
)

watch_lesson_2_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Посмотреть урок №2", url='https://rutube.ru/video/private/950a9fa5dbadec3786cf1ee7e313a30c/?p=FQ6Y7LWLs4ar2Ga72W3NWQ')],
    [InlineKeyboardButton(text="Перейти к следующему блоку", callback_data="next_block_2")],
    [InlineKeyboardButton(text='Назад', callback_data='back_list_4')],
]
)

next_block_2_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Смотреть урок №3", callback_data="watch_lesson_3")],
    [InlineKeyboardButton(text='Назад', callback_data='back_list_5')],
]
)

watch_lesson_3_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Посмотреть урок №3", url='https://rutube.ru/video/private/466be39bd6d7fc8607848b284ba9c922/?p=TN1XYAtYxgxTOXkKAdyQhw')],
    [InlineKeyboardButton(text="Перейти к следующему блоку", callback_data="next_block_3")],
    [InlineKeyboardButton(text='Назад', callback_data='back_list_6')],
]
)

next_block_3_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Заполнить анкету", url='https://docs.google.com/forms/d/12ZihHR79KLyMOy_qNadigH-K48MTtvoBSiL5qUXaOo0/viewform')],
    [InlineKeyboardButton(text="Консультация", callback_data="consultation")],
    [InlineKeyboardButton(text='Назад', callback_data='back_list_7')],
]
)

back_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Назад', callback_data='next_block_3')],
    ]
)

consultation_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Назад', callback_data='back_list_8')],
    ]
)
