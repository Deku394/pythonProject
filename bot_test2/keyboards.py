#вёрстка клавиатур keyboards.py
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

start_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Консультация", callback_data="consultation"),
     InlineKeyboardButton(text="Мой ТГ-канал", url="https://t.me/Sofika1231")],
    [InlineKeyboardButton(text="Акции", callback_data='action'),
     InlineKeyboardButton(text="Услуги", callback_data="services")],
    [InlineKeyboardButton(text='Локация и интерьер', callback_data='location_and_interior')],
]
)

consultation_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Главное меню', callback_data='back_menu')],
    ]
)

action_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Главное меню', callback_data='back_menu')],
    ]
)

services_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Снятие покрытия', callback_data='removing_the_coating'),
         InlineKeyboardButton(text='Гигиенический маникюр', callback_data='hygienic_manicure')],
        [InlineKeyboardButton(text='Маникюр с покрытием', callback_data='coated_manicure'),
         InlineKeyboardButton(text='Наращивание', callback_data='build_up')],
        [InlineKeyboardButton(text='Френч', callback_data='french'),
         InlineKeyboardButton(text='Маникюр с дизайном', callback_data='manicure_with_design')],
        [InlineKeyboardButton(text='Отзывы', callback_data='reviews'),
         InlineKeyboardButton(text='Прайс-лист', callback_data='price_list')],
        [InlineKeyboardButton(text='Главное меню', callback_data='back_menu')]
    ]
)

location_and_interior_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Локация', callback_data='location'),
         InlineKeyboardButton(text='Интерьер', callback_data='interior')],
        [InlineKeyboardButton(text='Главное меню', callback_data='back_menu')],
    ]
)

location_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Назад', callback_data='location_back_list'),
         InlineKeyboardButton(text='Главное меню', callback_data='back_menu')]
    ]
)

interior_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Назад', callback_data='interior_back_list'),
         InlineKeyboardButton(text='Главное меню', callback_data='back_menu')]
    ]
)

#Снятие покрытия

removing_the_coating_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Записаться', callback_data='sign_up_removing_the_coating')],
        [InlineKeyboardButton(text='Назад', callback_data='removing_the_coating_back_list'),
         InlineKeyboardButton(text='Главное меню', callback_data='back_menu')]
    ]
)

reviews_removing_the_coating_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Назад', callback_data='reviews_removing_the_coating_back_list')],
        [InlineKeyboardButton(text='Главное меню', callback_data='back_menu')]
    ]
)

sign_up_removing_the_coating_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Назад', callback_data='sign_up_removing_the_coating_back_list')],
        [InlineKeyboardButton(text='Главное меню', callback_data='back_menu')]
    ]
)

#Гигиенический маникюр

hygienic_manicure_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Записаться', callback_data='sign_up_hygienic_manicure')],
        [InlineKeyboardButton(text='Назад', callback_data='hygienic_manicure_back_list'),
         InlineKeyboardButton(text='Главное меню', callback_data='back_menu')]
    ]
)

reviews_hygienic_manicure_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Назад', callback_data='reviews_hygienic_manicure_back_list')],
        [InlineKeyboardButton(text='Главное меню', callback_data='back_menu')]
    ]
)

sign_up_hygienic_manicure_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Назад', callback_data='sign_up_hygienic_manicure_back_list')],
        [InlineKeyboardButton(text='Главное меню', callback_data='back_menu')]
    ]
)

#Маникюр с покрытием
coated_manicure_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Записаться', callback_data='sign_up_coated_manicure')],
        [InlineKeyboardButton(text='Назад', callback_data='coated_manicure_back_list'),
         InlineKeyboardButton(text='Главное меню', callback_data='back_menu')]
    ]
)

reviews_coated_manicure_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Назад', callback_data='reviews_coated_manicure_back_list')],
        [InlineKeyboardButton(text='Главное меню', callback_data='back_menu')]
    ]
)

sign_up_coated_manicure_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Назад', callback_data='sign_up_coated_manicure_back_list')],
        [InlineKeyboardButton(text='Главное меню', callback_data='back_menu')]
    ]
)

#Наращивание
build_up_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Записаться', callback_data='sign_up_build_up')],
        [InlineKeyboardButton(text='Назад', callback_data='build_up_back_list'),
         InlineKeyboardButton(text='Главное меню', callback_data='back_menu')]
    ]
)

reviews_build_up_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Назад', callback_data='reviews_build_up_back_list')],
        [InlineKeyboardButton(text='Главное меню', callback_data='back_menu')]
    ]
)

sign_up_build_up_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Назад', callback_data='sign_up_build_up_back_list')],
        [InlineKeyboardButton(text='Главное меню', callback_data='back_menu')]
    ]
)

#Френч
french_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Записаться', callback_data='sign_up_french')],
        [InlineKeyboardButton(text='Назад', callback_data='french_back_list'),
         InlineKeyboardButton(text='Главное меню', callback_data='back_menu')]
    ]
)

reviews_french_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Назад', callback_data='reviews_french_back_list')],
        [InlineKeyboardButton(text='Главное меню', callback_data='back_menu')]
    ]
)

sign_up_french_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Назад', callback_data='sign_up_french_back_list')],
        [InlineKeyboardButton(text='Главное меню', callback_data='back_menu')]
    ]
)

#Маникюр с дизайном

manicure_with_design_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Записаться', callback_data='sign_up_manicure_with_design')],
        [InlineKeyboardButton(text='Назад', callback_data='manicure_with_design_back_list'),
         InlineKeyboardButton(text='Главное меню', callback_data='back_menu')]
    ]
)

reviews_manicure_with_design_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Назад', callback_data='reviews_manicure_with_design_back_list')],
        [InlineKeyboardButton(text='Главное меню', callback_data='back_menu')]
    ]
)

sign_up_manicure_with_design_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Назад', callback_data='sign_up_manicure_with_design_back_list')],
        [InlineKeyboardButton(text='Главное меню', callback_data='back_menu')]
    ]
)

#отзывы

reviews_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Назад', callback_data='price_list_back_list_1'),
         InlineKeyboardButton(text='Главное меню', callback_data='back_menu')]
    ]
)

#прайс

price_list_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Записаться', url='https://t.me/SofiaFosterr')],
        [InlineKeyboardButton(text='Назад', callback_data='price_list_back_list_1'),
         InlineKeyboardButton(text='Главное меню', callback_data='back_menu')]
    ]
)

consultation_back_menu_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Главное меню', callback_data='back_menu')]
    ]
)

registration_back_menu_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Главное меню', callback_data='back_menu')]
    ]
)
