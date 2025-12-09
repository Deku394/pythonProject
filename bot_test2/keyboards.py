#вёрстка клавиатур
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

start_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Начать", callback_data="begin")],
]
)

begin_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Посмотреть урок №1", url='https://vk.com/video-220648156_456239061?list=ln-l89EmILIiLob9QSiwP')],
    [InlineKeyboardButton(text="Перейти к следующему блоку", callback_data="next_block_1")],
    [InlineKeyboardButton(text='Назад', callback_data='back_list_1')],
]
)

next_block_1_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Смотреть урок №2", callback_data="watch_lesson_2")],
    [InlineKeyboardButton(text='Назад', callback_data='back_list_2')],
]
)

watch_lesson_2_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Смотреть урок №2", url='https://vk.com/video-220648156_456239062?list=ln-LGpmsDN5AvsjbYTWZt')],
    [InlineKeyboardButton(text="Перейти к следующему уроку", callback_data="next_block_2")],
    [InlineKeyboardButton(text='Назад', callback_data='back_list_3')],
]
)

next_block_2_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Получить подарок", callback_data="get_gift")],
    [InlineKeyboardButton(text='Назад', callback_data='back_list_4')],
]
)

get_gift_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Заполнить анкету", url='https://s.bothelp.io/r/7u0bje.25l')],
    [InlineKeyboardButton(text="Консультация", callback_data="consultation")],
    [InlineKeyboardButton(text='Назад', callback_data='back_list_5')],
]
)

back_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Назад', callback_data='get_gift')],
    ]
)

consultation_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Назад', callback_data='back_list_6')],
    ]
)
