from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import asyncio
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from crud_functions import get_all_products

api = ''
bot = Bot(token=api)
dp = Dispatcher(bot, storage=MemoryStorage())

class UserState(StatesGroup):
    age = State()
    growth = State()
    weight = State()

kb = ReplyKeyboardMarkup(resize_keyboard=True)
button1 = KeyboardButton(text='Информация')
button2 = KeyboardButton(text='Рассчитать')
button3 = KeyboardButton(text='Купить')
kb.add(button1)
kb.add(button2)
kb.add(button3)

inline_kb = InlineKeyboardMarkup()
inline_button1 = InlineKeyboardButton(text='Рассчитать норму калорий', callback_data='calories')
inline_button2 = InlineKeyboardButton(text='Формулы расчёта', callback_data='formulas')
inline_kb.add(inline_button1)
inline_kb.add(inline_button2)

inline_kb_1 = InlineKeyboardMarkup()
inline_button_1 = InlineKeyboardButton(text='Product1', callback_data='product_buying')
inline_button_2 = InlineKeyboardButton(text='Product2', callback_data='product_buying')
inline_button_3 = InlineKeyboardButton(text='Product3', callback_data='product_buying')
inline_button_4 = InlineKeyboardButton(text='Product4', callback_data='product_buying')
inline_kb_1.add(inline_button_1)
inline_kb_1.add(inline_button_2)
inline_kb_1.add(inline_button_3)
inline_kb_1.add(inline_button_4)

start_menu = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='расчета калорий для мужчин'), KeyboardButton(text='расчета калорий для женщин'), KeyboardButton(text='')]],
                                 resize_keyboard=True)

@dp.callback_query_handler(text='calories')
async def set_age(call):
    await call.message.answer('Введите свой возраст:')
    await UserState.age.set()

@dp.message_handler(state=UserState.age)
async def set_growth(message, state):
    await state.update_data(first=message.text)
    await message.answer('Введите свой рост:')
    await UserState.growth.set()

@dp.message_handler(state=UserState.growth)
async def set_weight(message, state):
    await state.update_data(second=message.text)
    await message.answer('Введите свой вес:')
    await UserState.weight.set()

@dp.message_handler(state=UserState.weight)
async def send_calories(message, state):
    await state.update_data(third=message.text)
    data = await state.get_data()
    result = round(10*int(data['third']) + 6.25*int(data['second']) - 5*int(data['first']) + 5, 2)
    await message.answer(result)
    await state.finish()

@dp.message_handler(commands=['start'])
async def start(message):
    await message.answer('Йоу!', reply_markup=kb)

@dp.message_handler(text='Информация')
async def inform(message):
    await message.answer('Информация')

@dp.message_handler(text='Рассчитать')
async def main_menu(message):
    await message.answer('Выберите опцию:', reply_markup=inline_kb)

@dp.message_handler(text='Купить')
async def get_buying_list(message):
    for i in get_all_products():
        id = i[0]
        title = i[1]
        description = i[2]
        price = i[3]
        with open(f'{id}.png', 'rb') as img:
            await message.answer_photo(img, f'Название: {title} | Описание: {description} | Цена: {price}')
    await message.answer('Выберите продукт для покупки: ', reply_markup=inline_kb_1)

@dp.callback_query_handler(text='product_buying')
async def send_confirm_message(call):
    await call.message.answer('Вы успешно приобрели продукт!')

@dp.callback_query_handler(text='formulas')
async def get_formulas(call):
    await call.message.answer('Упрощенный вариант формулы Миффлина-Сан Жеора (для мужчин):'
                              ' 10 х вес (кг) + 6,25 x рост (см) – 5 х возраст (г) + 5')
    await call.answer()



if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)