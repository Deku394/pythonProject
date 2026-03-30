# mainbot.py
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.utils.exceptions import MessageNotModified
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from keyboards import *  # Предполагается, что этот файл существует и содержит определения клавиатур
from texst import *  # Предполагается, что этот файл существует и содержит определения текстов
import logging
import json
import os
import calendar
import sqlite3
import re
import asyncio
import pytz
from datetime import datetime, date, timedelta

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# ВНИМАНИЕ: Замените на ваш реальный API-токен бота
api = '8081851926:AAFGhM39fmpjZVFH-WPd2T2jyD-1sI8z-m4'
bot_tests = Bot(token=api)
dp = Dispatcher(bot_tests, storage=MemoryStorage())

ADMIN_ID = 1060502535  # замените при необходимости

DB_FILE = 'registered_users.json'
registered_users = {}
last_message_id = None


def load_registered_users():
    global registered_users
    if os.path.exists(DB_FILE) and os.path.getsize(DB_FILE) > 0:
        with open(DB_FILE, 'r', encoding='utf-8') as f:
            try:
                registered_users = json.load(f)
                logging.info(f"Загружено {len(registered_users)} пользователей из {DB_FILE}")
            except Exception:
                registered_users = {}
    else:
        registered_users = {}


def save_registered_users():
    try:
        with open(DB_FILE, 'w', encoding='utf-8') as f:
            json.dump(registered_users, f, ensure_ascii=False, indent=4)
    except Exception as e:
        logging.error(f"Ошибка при сохранении пользователей: {e}")


load_registered_users()


class AdminStates(StatesGroup):
    waiting_for_users_selection = State()
    waiting_for_message = State()
    waiting_for_media = State()
    waiting_for_user_id_to_delete = State()
    waiting_for_appointment_id_to_cancel = State()


# --------------------------------------------------------------------------------------------------
# Handlers
# --------------------------------------------------------------------------------------------------

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    user_id = str(message.from_user.id)
    name = message.from_user.full_name
    custom_name = message.from_user.username

    if user_id not in registered_users:
        registered_users[user_id] = {'name': name, 'custom_name': custom_name}
        save_registered_users()
    else:
        cur = registered_users[user_id]
        if cur.get('name') != name or cur.get('custom_name') != custom_name:
            registered_users[user_id]['name'] = name
            registered_users[user_id]['custom_name'] = custom_name
            save_registered_users()

    global last_message_id
    if last_message_id:
        try:
            await bot_tests.delete_message(chat_id=message.chat.id, message_id=last_message_id)
        except Exception:
            pass  # Игнорируем ошибку, если сообщение уже удалено или не найдено

    try:
        with open('photo_1.jpg', 'rb') as img:
            new_message = await message.answer_photo(img,
                                                     f'Добро пожаловать, {message.from_user.full_name}! 👋🏻\n' +
                                                     start_text,  # start_text должен быть определен в texst.py
                                                     parse_mode=types.ParseMode.HTML,
                                                     reply_markup=start_kb)  # start_kb должен быть определен в keyboards.py
            last_message_id = new_message.message_id
    except Exception:
        await message.reply("Добро пожаловать! 👋🏻", reply_markup=start_kb)


@dp.message_handler(commands=['admin'])
async def cmd_admin(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("▫️К сожалению, у вас нет доступа к админ-панели! 😞")
        return

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add("Отправить сообщение всем", "Отправить сообщение выбранным")
    keyboard.add("Список пользователей", "Удалить пользователя")
    keyboard.add("Мои записи")
    keyboard.add("Главное меню")
    await message.answer(f"▫️Добро пожаловать в панель администратора, {message.from_user.full_name}! 👋🏻",
                         reply_markup=keyboard)


@dp.message_handler(lambda message: message.text == "Список пользователей")
async def list_users(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        await message.reply("▫️У вас нет доступа к этой функции! 😞")
        return

    if not registered_users:
        await message.reply("▫️К сожалению, у вас еще нет зарегистрированных пользователей. 😞")
        return

    user_list_str = "Список зарегистрированных пользователей:\n"
    part = ""
    for index, (user_id, user_data) in enumerate(registered_users.items()):
        line = f"{index + 1}.\n▫️ID: {user_id};\n▫️Имя: {user_data.get('name', 'Не указано')};\n▫️Имя (через @): @{user_data.get('custom_name', 'Не указано')}\n"
        if len(part) + len(line) > 4000:  # Telegram message limit
            await message.reply(part)
            part = ""
        part += line
    if part:
        await message.reply(part)


@dp.message_handler(lambda message: message.text == "Отправить сообщение выбранным")
async def select_users_to_send_message(message: types.Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        await message.reply("▫️К сожалению, у вас нет доступа к этой функции! 😞")
        return

    await AdminStates.waiting_for_users_selection.set()
    if not registered_users:
        await message.reply("▫️К сожалению, у вас еще нет зарегистрированных пользователей для отправки сообщений. 😞")
        await message.finish()
        return

    user_list_str = "▫️Выберите, пожалуйста, пользователя(ей) по ID, которому(ым) хотите отправить сообщение.\n▫️Чтобы отправить сообщение нескольким пользователям, напишите ID пользователей через запятую: 👇🏼\n\n"
    for index, (user_id, user_data) in enumerate(registered_users.items()):
        user_list_str += f"{index + 1}.\n▫️ID: {user_id};\n▫️Имя: {user_data.get('name', 'Не указано')};\n▫️Имя (через @): @{user_data.get('custom_name', 'Не указано')}\n"
    await message.reply(user_list_str)


@dp.message_handler(state=AdminStates.waiting_for_users_selection,
                    content_types=[types.ContentType.TEXT])
async def process_selected_users_message(message: types.Message, state: FSMContext):
    user_ids_input = message.text.strip().split(',')
    valid_user_ids = []
    for user_id_str in user_ids_input:
        user_id_str = user_id_str.strip()
        if user_id_str.isdigit() and user_id_str in registered_users:
            valid_user_ids.append(user_id_str)

    if not valid_user_ids:
        await message.reply("▫️Нет валидных ID пользователей! Попробуйте, пожалуйста, снова: 👇🏼")
        await state.finish()
        return

    await state.update_data(valid_user_ids=valid_user_ids)
    await AdminStates.waiting_for_media.set()
    await message.reply("▫️Введите, пожалуйста, сообщение для выбранного(ых) пользователя(ей) (сообщение может быть любого формата): 👇🏼")


@dp.message_handler(state=AdminStates.waiting_for_media,
                    content_types=[types.ContentType.ANY])
async def process_message_to_selected(message: types.Message, state: FSMContext):
    data = await state.get_data()
    valid_user_ids = data.get('valid_user_ids', [])

    if not valid_user_ids:
        await message.reply("▫️К сожалению, не было выбрано ни одного пользователя. 😞")
        await state.finish()
        return

    sent_count = 0
    failed = []
    for user_id_str in valid_user_ids:
        try:
            user_id_int = int(user_id_str)
            if message.content_type == types.ContentType.TEXT:
                await bot_tests.send_message(user_id_int, message.text)
            elif message.content_type == types.ContentType.PHOTO:
                await bot_tests.send_photo(user_id_int, message.photo[-1].file_id,
                                           caption=message.caption)
            elif message.content_type == types.ContentType.VIDEO:
                await bot_tests.send_video(user_id_int, message.video.file_id, caption=message.caption)
            elif message.content_type == types.ContentType.AUDIO:
                await bot_tests.send_audio(user_id_int, message.audio.file_id, caption=message.caption)
            elif message.content_type == types.ContentType.VOICE:
                await bot_tests.send_voice(user_id_int, message.voice.file_id, caption=message.caption)
            elif message.content_type == types.ContentType.STICKER:
                await bot_tests.send_sticker(user_id_int, message.sticker.file_id)
            elif message.content_type == types.ContentType.VIDEO_NOTE:
                await bot_tests.send_video_note(user_id_int, message.video_note.file_id)
            elif message.content_type == types.ContentType.DOCUMENT:
                await bot_tests.send_document(user_id_int, message.document.file_id,
                                              caption=message.caption)
            sent_count += 1
        except Exception:
            failed.append(user_id_str)

    await message.reply(f"▫️Сообщение было отправлено (количество пользователей, которым было отправлено сообщение): {sent_count}.\n\n▫️Ошибки при отправке сообщения: {', '.join(failed) if failed else 'нет'}")
    await state.finish()


@dp.message_handler(lambda message: message.text == "Отправить сообщение всем")
async def send_message_to_all(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        await message.reply("▫️К сожалению, у вас нет доступа к этой функции! 😞")
        return

    await AdminStates.waiting_for_message.set()
    await message.reply("▫️Введите, пожалуйста, сообщение для всех зарегистрированных пользователей (сообщение может быть любого формата): 👇🏼")


@dp.message_handler(state=AdminStates.waiting_for_message,
                    content_types=[types.ContentType.ANY])
async def process_message_to_all(message: types.Message, state: FSMContext):
    sent_count = 0
    failed = []
    for user_id_str in list(registered_users.keys()):
        try:
            user_id_int = int(user_id_str)
            if message.content_type == types.ContentType.TEXT:
                await bot_tests.send_message(user_id_int, message.text)
            elif message.content_type == types.ContentType.PHOTO:
                await bot_tests.send_photo(user_id_int, message.photo[-1].file_id,
                                           caption=message.caption)
            elif message.content_type == types.ContentType.VIDEO:
                await bot_tests.send_video(user_id_int, message.video.file_id, caption=message.caption)
            elif message.content_type == types.ContentType.AUDIO:
                await bot_tests.send_audio(user_id_int, message.audio.file_id, caption=message.caption)
            elif message.content_type == types.ContentType.VOICE:
                await bot_tests.send_voice(user_id_int, message.voice.file_id, caption=message.caption)
            elif message.content_type == types.ContentType.STICKER:
                await bot_tests.send_sticker(user_id_int, message.sticker.file_id)
            elif message.content_type == types.ContentType.VIDEO_NOTE:
                await bot_tests.send_video_note(user_id_int, message.video_note.file_id)
            elif message.content_type == types.ContentType.DOCUMENT:
                await bot_tests.send_document(user_id_int, message.document.file_id,
                                              caption=message.caption)
            sent_count += 1
        except Exception:
            failed.append(user_id_str)

    await message.reply(f"▫️Сообщение было отправлено всем пользователям (количество пользователей, которым было отправлено сообщение): {sent_count}.\n\n▫️Ошибки при отправке сообщения: {', '.join(failed) if failed else 'нет'}")
    await state.finish()


@dp.message_handler(lambda message: message.text == "Удалить пользователя")
async def delete_user(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        await message.reply("▫️К сожалению, у вас нет доступа к этой функции! 😞")
        return

    await AdminStates.waiting_for_user_id_to_delete.set()
    if not registered_users:
        await message.reply("▫️К сожалению, у вас нет зарегистрированных пользователей для удаления. 😞")
        await message.finish()
        return

    user_list_str = "▫️Введите, пожалуйста, ID пользователя, которого хотите удалить: 👇🏼\n"
    for index, (user_id, user_data) in enumerate(registered_users.items()):
        user_list_str += f"{index + 1}.\n▫️ID: {user_id};\n▫️Имя: {user_data.get('name', 'Не указано')};\n▫️Имя (через @): @{user_data.get('custom_name', 'Не указано')}\n"
    await message.reply(user_list_str)


@dp.message_handler(state=AdminStates.waiting_for_user_id_to_delete,
                    content_types=[types.ContentType.TEXT])
async def remove_user(message: types.Message, state: FSMContext):
    user_id_to_delete = message.text.strip()
    if user_id_to_delete in registered_users:
        del registered_users[user_id_to_delete]
        save_registered_users()
        await message.reply(f"▫️Пользователь с ID: {user_id_to_delete} был успешно удален! 🤗")
    else:
        await message.reply("▫️К сожалению, пользователь с таким ID не найден! 😞")
    await state.finish()


@dp.message_handler(lambda message: message.text == "Главное меню", state="*")
async def back_to_main_menu(message: types.Message, state: FSMContext):
    await state.finish()
    global last_message_id
    if last_message_id:
        try:
            await bot_tests.delete_message(chat_id=message.chat.id, message_id=last_message_id)
        except Exception:
            pass
    try:
        with open('photo_1.jpg', 'rb') as img:
            new_message = await message.answer_photo(img,
                                                     f'Добро пожаловать, {message.from_user.full_name}! 👋🏻\n' +
                                                     start_text,
                                                     parse_mode=types.ParseMode.HTML, reply_markup=start_kb)
            last_message_id = new_message.message_id
    except Exception:
        await message.reply("Добро пожаловать! 👋🏻", reply_markup=start_kb)


@dp.message_handler(lambda message: message.text == "Главное меню")
async def back_to_main_menu_simple(message: types.Message):
    await start(message)


@dp.callback_query_handler(text='consultation')
async def consultation(call: types.CallbackQuery):
    global last_message_id
    if last_message_id:
        try:
            await bot_tests.delete_message(chat_id=call.message.chat.id, message_id=last_message_id)
        except Exception:
            pass
    try:
        with open('photo_consultation.jpg', 'rb') as img:
            new_message = await call.message.answer_photo(img, consultation_text,
                                                          reply_markup=consultation_kb)
            last_message_id = new_message.message_id
    except Exception:
        await call.message.answer(consultation_text, reply_markup=consultation_kb)
    await call.answer()


# Примеры callback handlers (оставлены все ваши callback handlers — сократил вывод для читаемости)
@dp.callback_query_handler(text='action')
async def action(call: types.CallbackQuery):
    global last_message_id
    if last_message_id:
        try:
            await bot_tests.delete_message(chat_id=call.message.chat.id, message_id=last_message_id)
        except Exception:
            pass
    try:
        with open('photo_action.jpg', 'rb') as img:
            new_message = await call.message.answer_photo(img, action_text,
                                                          parse_mode=types.ParseMode.HTML, reply_markup=action_kb)
            last_message_id = new_message.message_id
    except Exception:
        await call.message.answer(action_text, reply_markup=action_kb)
    await call.answer()


@dp.callback_query_handler(text='services')
async def services(call):
    global last_message_id  # Объявляем переменную как глобальную
    # Удаляем предыдущее сообщение, если оно существует
    if last_message_id:
        try:
            await bot_tests.delete_message(chat_id=call.message.chat.id, message_id=last_message_id)
        except Exception as e:
            logging.error(f"Ошибка при удалении сообщения: {e}")
    with open('photo_services.jpg', 'rb') as img:
        new_message = await call.message.answer_photo(img, services_text,
                                                      parse_mode=types.ParseMode.HTML, reply_markup=services_kb)
    last_message_id = new_message.message_id  # Сохраняем ID нового сообщения
    await call.answer()


@dp.callback_query_handler(text='location_and_interior')
async def location_and_interior(call):
    global last_message_id  # Объявляем переменную как глобальную
    # Удаляем предыдущее сообщение, если оно существует
    if last_message_id:
        try:
            await bot_tests.delete_message(chat_id=call.message.chat.id, message_id=last_message_id)
        except Exception as e:
            logging.error(f"Ошибка при удалении сообщения: {e}")
    with open('photo_location_interior.jpg', 'rb') as img:
        new_message = await call.message.answer_photo(img, location_and_interior_text,
                                                      parse_mode=types.ParseMode.HTML,
                                                      reply_markup=location_and_interior_kb)
    last_message_id = new_message.message_id  # Сохраняем ID нового сообщения
    await call.answer()


@dp.callback_query_handler(text='location')
async def location(call):
    global last_message_id  # Объявляем переменную как глобальную
    # Удаляем предыдущее сообщение, если оно существует
    if last_message_id:
        try:
            await bot_tests.delete_message(chat_id=call.message.chat.id, message_id=last_message_id)
        except Exception as e:
            logging.error(f"Ошибка при удалении сообщения: {e}")
    with open('photo_location.jpg', 'rb') as img:
        new_message = await call.message.answer_photo(img, location_text,
                                                      parse_mode=types.ParseMode.HTML, reply_markup=location_kb)
    last_message_id = new_message.message_id  # Сохраняем ID нового сообщения
    await call.answer()


@dp.callback_query_handler(text='location_back_list')
async def location_back_list(call):
    global last_message_id  # Объявляем переменную как глобальную
    # Удаляем предыдущее сообщение, если оно существует
    if last_message_id:
        try:
            await bot_tests.delete_message(chat_id=call.message.chat.id, message_id=last_message_id)
        except Exception as e:
            logging.error(f"Ошибка при удалении сообщения: {e}")
    with open('photo_location_interior.jpg', 'rb') as img:
        new_message = await call.message.answer_photo(img, location_and_interior_text,
                                                      parse_mode=types.ParseMode.HTML,
                                                      reply_markup=location_and_interior_kb)
    last_message_id = new_message.message_id  # Сохраняем ID нового сообщения
    await call.answer()


@dp.callback_query_handler(text='interior')
async def interior(call):
    global last_message_id  # Объявляем переменную как глобальную
    # Удаляем предыдущее сообщение, если оно существует
    if last_message_id:
        try:
            await bot_tests.delete_message(chat_id=call.message.chat.id, message_id=last_message_id)
        except Exception as e:
            logging.error(f"Ошибка при удалении сообщения: {e}")
    with open('photo_interior.jpg', 'rb') as img:
        new_message = await call.message.answer_photo(img, interior_text,
                                                      parse_mode=types.ParseMode.HTML,
                                                      reply_markup=interior_kb)
    last_message_id = new_message.message_id  # Сохраняем ID нового сообщения
    await call.answer()


@dp.callback_query_handler(text='interior_back_list')
async def interior_back_list(call):
    global last_message_id  # Объявляем переменную как глобальную
    # Удаляем предыдущее сообщение, если оно существует
    if last_message_id:
        try:
            await bot_tests.delete_message(chat_id=call.message.chat.id, message_id=last_message_id)
        except Exception as e:
            logging.error(f"Ошибка при удалении сообщения: {e}")
    with open('photo_location_interior.jpg', 'rb') as img:
        new_message = await call.message.answer_photo(img, location_and_interior_text,
                                                      parse_mode=types.ParseMode.HTML,
                                                      reply_markup=location_and_interior_kb)
    last_message_id = new_message.message_id  # Сохраняем ID нового сообщения
    await call.answer()


@dp.callback_query_handler(text='removing_the_coating')
async def removing_the_coating(call):
    global last_message_id  # Объявляем переменную как глобальную
    # Удаляем предыдущее сообщение, если оно существует
    if last_message_id:
        try:
            await bot_tests.delete_message(chat_id=call.message.chat.id, message_id=last_message_id)
        except Exception as e:
            logging.error(f"Ошибка при удалении сообщения: {e}")
    with open('photo_removing_the_coating.jpg', 'rb') as img:
        new_message = await call.message.answer_photo(img, removing_the_coating_text,
                                                      parse_mode=types.ParseMode.HTML,
                                                      reply_markup=removing_the_coating_kb)
    last_message_id = new_message.message_id  # Сохраняем ID нового сообщения
    await call.answer()


@dp.callback_query_handler(text='removing_the_coating_back_list')
async def removing_the_coating_back_list(call):
    global last_message_id  # Объявляем переменную как глобальную
    # Удаляем предыдущее сообщение, если оно существует
    if last_message_id:
        try:
            await bot_tests.delete_message(chat_id=call.message.chat.id, message_id=last_message_id)
        except Exception as e:
            logging.error(f"Ошибка при удалении сообщения: {e}")
    with open('photo_services.jpg', 'rb') as img:
        new_message = await call.message.answer_photo(img, services_text,
                                                      parse_mode=types.ParseMode.HTML,
                                                      reply_markup=services_kb)
    last_message_id = new_message.message_id  # Сохраняем ID нового сообщения
    await call.answer()


@dp.callback_query_handler(text='hygienic_manicure')
async def hygienic_manicure(call):
    global last_message_id  # Объявляем переменную как глобальную
    # Удаляем предыдущее сообщение, если оно существует
    if last_message_id:
        try:
            await bot_tests.delete_message(chat_id=call.message.chat.id, message_id=last_message_id)
        except Exception as e:
            logging.error(f"Ошибка при удалении сообщения: {e}")
    with open('photo_hygienic_manicure.jpg', 'rb') as img:
        new_message = await call.message.answer_photo(img, hygienic_manicure_text,
                                                      parse_mode=types.ParseMode.HTML,
                                                      reply_markup=hygienic_manicure_kb)
    last_message_id = new_message.message_id  # Сохраняем ID нового сообщения
    await call.answer()


@dp.callback_query_handler(text='hygienic_manicure_back_list')
async def hygienic_manicure_back_list(call):
    global last_message_id  # Объявляем переменную как глобальную
    # Удаляем предыдущее сообщение, если оно существует
    if last_message_id:
        try:
            await bot_tests.delete_message(chat_id=call.message.chat.id, message_id=last_message_id)
        except Exception as e:
            logging.error(f"Ошибка при удалении сообщения: {e}")
    with open('photo_services.jpg', 'rb') as img:
        new_message = await call.message.answer_photo(img, services_text,
                                                      parse_mode=types.ParseMode.HTML,
                                                      reply_markup=services_kb)
    last_message_id = new_message.message_id  # Сохраняем ID нового сообщения
    await call.answer()


@dp.callback_query_handler(text='coated_manicure')
async def coated_manicure(call):
    global last_message_id  # Объявляем переменную как глобальную
    # Удаляем предыдущее сообщение, если оно существует
    if last_message_id:
        try:
            await bot_tests.delete_message(chat_id=call.message.chat.id, message_id=last_message_id)
        except Exception as e:
            logging.error(f"Ошибка при удалении сообщения: {e}")
    with open('photo_coated_manicure.jpg', 'rb') as img:
        new_message = await call.message.answer_photo(img, coated_manicure_text,
                                                      parse_mode=types.ParseMode.HTML, reply_markup=coated_manicure_kb)
    last_message_id = new_message.message_id  # Сохраняем ID нового сообщения
    await call.answer()


@dp.callback_query_handler(text='coated_manicure_back_list')
async def coated_manicure_back_list(call):
    global last_message_id  # Объявляем переменную как глобальную
    # Удаляем предыдущее сообщение, если оно существует
    if last_message_id:
        try:
            await bot_tests.delete_message(chat_id=call.message.chat.id, message_id=last_message_id)
        except Exception as e:
            logging.error(f"Ошибка при удалении сообщения: {e}")
    with open('photo_services.jpg', 'rb') as img:
        new_message = await call.message.answer_photo(img, services_text,
                                                      parse_mode=types.ParseMode.HTML,
                                                      reply_markup=services_kb)
    last_message_id = new_message.message_id  # Сохраняем ID нового сообщения
    await call.answer()


@dp.callback_query_handler(text='build_up')
async def build_up(call):
    global last_message_id  # Объявляем переменную как глобальную
    # Удаляем предыдущее сообщение, если оно существует
    if last_message_id:
        try:
            await bot_tests.delete_message(chat_id=call.message.chat.id, message_id=last_message_id)
        except Exception as e:
            logging.error(f"Ошибка при удалении сообщения: {e}")
    with open('photo_build_up.jpg', 'rb') as img:
        new_message = await call.message.answer_photo(img, build_up_text,
                                                      parse_mode=types.ParseMode.HTML, reply_markup=build_up_kb)
    last_message_id = new_message.message_id  # Сохраняем ID нового сообщения
    await call.answer()


@dp.callback_query_handler(text='build_up_back_list')
async def build_up_back_list(call):
    global last_message_id  # Объявляем переменную как глобальную
    # Удаляем предыдущее сообщение, если оно существует
    if last_message_id:
        try:
            await bot_tests.delete_message(chat_id=call.message.chat.id, message_id=last_message_id)
        except Exception as e:
            logging.error(f"Ошибка при удалении сообщения: {e}")
    with open('photo_services.jpg', 'rb') as img:
        new_message = await call.message.answer_photo(img, services_text,
                                                      parse_mode=types.ParseMode.HTML,
                                                      reply_markup=services_kb)
    last_message_id = new_message.message_id  # Сохраняем ID нового сообщения
    await call.answer()


@dp.callback_query_handler(text='french')
async def french(call):
    global last_message_id  # Объявляем переменную как глобальную
    # Удаляем предыдущее сообщение, если оно существует
    if last_message_id:
        try:
            await bot_tests.delete_message(chat_id=call.message.chat.id, message_id=last_message_id)
        except Exception as e:
            logging.error(f"Ошибка при удалении сообщения: {e}")
    with open('photo_french.jpg', 'rb') as img:
        new_message = await call.message.answer_photo(img, french_text,
                                                      parse_mode=types.ParseMode.HTML, reply_markup=french_kb)
    last_message_id = new_message.message_id  # Сохраняем ID нового сообщения
    await call.answer()


@dp.callback_query_handler(text='french_back_list')
async def french_back_list(call):
    global last_message_id  # Объявляем переменную как глобальную
    # Удаляем предыдущее сообщение, если оно существует
    if last_message_id:
        try:
            await bot_tests.delete_message(chat_id=call.message.chat.id, message_id=last_message_id)
        except Exception as e:
            logging.error(f"Ошибка при удалении сообщения: {e}")
    with open('photo_services.jpg', 'rb') as img:
        new_message = await call.message.answer_photo(img, services_text,
                                                      parse_mode=types.ParseMode.HTML,
                                                      reply_markup=services_kb)
    last_message_id = new_message.message_id  # Сохраняем ID нового сообщения
    await call.answer()


@dp.callback_query_handler(text='manicure_with_design')
async def manicure_with_design(call):
    global last_message_id  # Объявляем переменную как глобальную
    # Удаляем предыдущее сообщение, если оно существует
    if last_message_id:
        try:
            await bot_tests.delete_message(chat_id=call.message.chat.id, message_id=last_message_id)
        except Exception as e:
            logging.error(f"Ошибка при удалении сообщения: {e}")
    with open('photo_manicure_with_design.jpg', 'rb') as img:
        new_message = await call.message.answer_photo(img, manicure_with_design_text,
                                                      parse_mode=types.ParseMode.HTML,
                                                      reply_markup=manicure_with_design_kb)
    last_message_id = new_message.message_id  # Сохраняем ID нового сообщения
    await call.answer()


@dp.callback_query_handler(text='manicure_with_design_back_list')
async def manicure_with_design_back_list(call):
    global last_message_id  # Объявляем переменную как глобальную
    # Удаляем предыдущее сообщение, если оно существует
    if last_message_id:
        try:
            await bot_tests.delete_message(chat_id=call.message.chat.id, message_id=last_message_id)
        except Exception as e:
            logging.error(f"Ошибка при удалении сообщения: {e}")
    with open('photo_services.jpg', 'rb') as img:
        new_message = await call.message.answer_photo(img, services_text,
                                                      parse_mode=types.ParseMode.HTML,
                                                      reply_markup=services_kb)
    last_message_id = new_message.message_id  # Сохраняем ID нового сообщения
    await call.answer()


@dp.callback_query_handler(text='reviews')
async def reviews(call):
    global last_message_id  # Объявляем переменную как глобальную
    # Удаляем предыдущее сообщение, если оно существует
    if last_message_id:
        try:
            await bot_tests.delete_message(chat_id=call.message.chat.id, message_id=last_message_id)
        except Exception as e:
            logging.error(f"Ошибка при удалении сообщения: {e}")
    with open('photo_reviews.jpg', 'rb') as img:
        new_message = await call.message.answer_photo(img, reviews_text,
                                                      parse_mode=types.ParseMode.HTML, reply_markup=reviews_kb)
    last_message_id = new_message.message_id  # Сохраняем ID нового сообщения
    await call.answer()


@dp.callback_query_handler(text='reviews_back_list')
async def reviews_back_list(call):
    global last_message_id  # Объявляем переменную как глобальную
    # Удаляем предыдущее сообщение, если оно существует
    if last_message_id:
        try:
            await bot_tests.delete_message(chat_id=call.message.chat.id, message_id=last_message_id)
        except Exception as e:
            logging.error(f"Ошибка при удалении сообщения: {e}")
    with open('photo_services.jpg', 'rb') as img:
        new_message = await call.message.answer_photo(img, services_text,
                                                      parse_mode=types.ParseMode.HTML, reply_markup=services_kb)
    last_message_id = new_message.message_id  # Сохраняем ID нового сообщения
    await call.answer()


@dp.callback_query_handler(text='price_list')
async def price_list(call):
    global last_message_id  # Объявляем переменную как глобальную
    # Удаляем предыдущее сообщение, если оно существует
    if last_message_id:
        try:
            await bot_tests.delete_message(chat_id=call.message.chat.id, message_id=last_message_id)
        except Exception as e:
            logging.error(f"Ошибка при удалении сообщения: {e}")
    with open('photo_price.jpg', 'rb') as img:
        new_message = await call.message.answer_photo(img, price_list_text,
                                                      parse_mode=types.ParseMode.HTML, reply_markup=price_list_kb)
    last_message_id = new_message.message_id  # Сохраняем ID нового сообщения
    await call.answer()


@dp.callback_query_handler(text='price_list_back_list_1')
async def price_list_back_list_1(call):
    global last_message_id  # Объявляем переменную как глобальную
    # Удаляем предыдущее сообщение, если оно существует
    if last_message_id:
        try:
            await bot_tests.delete_message(chat_id=call.message.chat.id, message_id=last_message_id)
        except Exception as e:
            logging.error(f"Ошибка при удалении сообщения: {e}")
    with open('photo_services.jpg', 'rb') as img:
        new_message = await call.message.answer_photo(img, services_text,
                                                      parse_mode=types.ParseMode.HTML, reply_markup=services_kb)
    last_message_id = new_message.message_id  # Сохраняем ID нового сообщения
    await call.answer()


@dp.callback_query_handler(text='back_menu')
async def back_menu(call):
    global last_message_id  # Объявляем переменную как глобальную
    # Удаляем предыдущее сообщение, если оно существует
    if last_message_id:
        try:
            await bot_tests.delete_message(chat_id=call.message.chat.id, message_id=last_message_id)
        except Exception as e:
            logging.error(f"Ошибка при удалении сообщения: {e}")
    with open('photo_1.jpg', 'rb') as img:
        new_message = await call.message.answer_photo(img, f'Добро пожаловать,\n{call.from_user.full_name}!\n' +
                                                      start_text, parse_mode=types.ParseMode.HTML,
                                                      reply_markup=start_kb)
    last_message_id = new_message.message_id  # Сохраняем ID нового сообщения
    await call.answer()


# --------------------------------------------------------------------------------------------------
# Booking: SQLite + asyncio reminders
# --------------------------------------------------------------------------------------------------

TIMEZONE = "Europe/Moscow"
tz = pytz.timezone(TIMEZONE)
APPTS_DB = "appointments.db"
SLOTS_DEFAULT = ["09:00", "10:00", "11:00", "12:00", "13:00", "14:00", "15:00", "16:00", "17:00"]
NAV_MONTHS = 12

# Словарь для перевода технических ключей услуг в русский текст
SERVICES_MAP = {
    "coated_manicure": "Маникюр с покрытием",
    "hygienic_manicure": "Гигиенический маникюр",
    "build_up": "Наращивание ногтей",
    "french": "Френч",
    "manicure_with_design": "Маникюр с дизайном",
    "removing_the_coating": "Снятие покрытия",
    "consultation": "Консультация"
}

# Названия месяцев на русском
RUS_MONTHS = [
    "", "Январь", "Февраль", "Март", "Апрель", "Май", "Июнь",
    "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"
]

conn_appt = sqlite3.connect(APPTS_DB, check_same_thread=False)
cur_appt = conn_appt.cursor()
cur_appt.execute("""
CREATE TABLE IF NOT EXISTS appointments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    service TEXT,
    user_name TEXT,
    phone TEXT,
    comment TEXT,
    datetime TEXT,
    created_at TEXT
)
""")
conn_appt.commit()

GLOBAL_LOOP = None
GLOBAL_REMINDER_TASKS = {}
PHONE_RE = re.compile(r'^\+?\d{7,15}$')


class BookingStates(StatesGroup):
    waiting_name = State()
    waiting_phone = State()
    waiting_comment = State()
    waiting_consents = State()


def month_label(y, m):
    return f"{RUS_MONTHS[m].capitalize()} {y}"  # Используем RUS_MONTHS


def create_calendar(year: int, month: int, base_year: int, base_month: int):
    kb = InlineKeyboardMarkup(row_width=7)

    def month_diff(y, m, oy, om):
        return (y - oy) * 12 + (m - om)

    prev_month_date = (date(year, month, 1) - timedelta(days=1)).replace(day=1)
    next_month_date = (date(year, month, 28) + timedelta(days=10)).replace(day=1)

    prev_allowed = abs(month_diff(prev_month_date.year, prev_month_date.month, base_year,
                                  base_month)) <= NAV_MONTHS
    next_allowed = abs(month_diff(next_month_date.year, next_month_date.month, base_year,
                                  base_month)) <= NAV_MONTHS

    prev_cb = f"CAL|{prev_month_date.year}-{prev_month_date.month:02d}" if prev_allowed else "IGNORE"
    next_cb = f"CAL|{next_month_date.year}-{next_month_date.month:02d}" if next_allowed else "IGNORE"

    kb.row(InlineKeyboardButton("<", callback_data=prev_cb),
           InlineKeyboardButton(month_label(year, month), callback_data="IGNORE"),
           InlineKeyboardButton(">", callback_data=next_cb))

    days = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
    kb.row(*[InlineKeyboardButton(d, callback_data="IGNORE") for d in days])

    cal = calendar.Calendar(firstweekday=0).monthdayscalendar(year, month)
    today = datetime.now(tz).date()

    for week in cal:
        row = []
        for d in week:
            if d == 0:
                row.append(InlineKeyboardButton(" ", callback_data="IGNORE"))
            else:
                dt = date(year, month, d)
                if dt < today:
                    row.append(InlineKeyboardButton(str(d), callback_data="IGNORE"))
                else:
                    row.append(InlineKeyboardButton(str(d),
                                                    callback_data=f"DATE|{dt.strftime('%Y-%m-%d')}"))
        kb.row(*row)
    return kb


def times_kb_for_date(date_str: str):
    kb = InlineKeyboardMarkup(row_width=3)
    for t in SLOTS_DEFAULT:
        full_dt_str = f"{date_str} {t}"
        # ИЗМЕНЕНИЕ: Проверяем, свободен ли слот, и соответствующим образом меняем текст и callback_data
        if not is_slot_free(full_dt_str):  # Если слот ЗАНЯТ
            button_text = f"{t} ❌"  # Визуально помечаем как занятый
            callback_data = "IGNORE"  # Делаем кнопку неактивной
        else:  # Если слот СВОБОДЕН
            button_text = t
            callback_data = f"TIME|{date_str}|{t}"
        kb.insert(InlineKeyboardButton(button_text, callback_data=callback_data))
    kb.row(InlineKeyboardButton("Вернуться к выбору даты", callback_data="BACK_TO_CALENDAR"))
    return kb


def consents_kb(pd: bool, mail: bool):
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("✔ ПД" if pd else "Х ПД", callback_data="TOGGLE_PD"),
        InlineKeyboardButton("✔ Рассылка" if mail else "Х Рассылка", callback_data="TOGGLE_MAIL")
    )
    kb.add(InlineKeyboardButton("Записаться", callback_data="SUBMIT"))
    return kb


def parse_dt_local(date_str, time_str):
    naive = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
    return tz.localize(naive)


def is_slot_free(dt_str):
    cur_appt.execute("SELECT COUNT(*) FROM appointments WHERE datetime = ?", (dt_str,))
    return cur_appt.fetchone()[0] == 0


async def reminder_worker(appt_id: int, appt_dt: datetime):
    try:
        remind_at = appt_dt - timedelta(hours=2)
        now = datetime.now(tz)
        delay = (remind_at - now).total_seconds()

        if delay <= 0:
            return

        await asyncio.sleep(delay)

        try:
            c = sqlite3.connect(APPTS_DB, check_same_thread=False)
            cur = c.cursor()
            cur.execute("SELECT user_id, service, user_name, phone, comment, datetime FROM "
                        "appointments WHERE id=?", (appt_id,))
            row = cur.fetchone()
            c.close()
        except Exception:
            row = None

        if not row:
            return

        user_id, service_db, user_name, phone, comment, dt_str = row
        # ИЗМЕНЕНИЕ: Нормализуем ключ и переводим название услуги на русский язык перед использованием
        normalized_service_key = service_db.lower().replace(" ", "_")
        translated_service = SERVICES_MAP.get(normalized_service_key, service_db)

        user_text = (f"❕ Напоминание о записи!🕰\n▫️Услуга: {translated_service}\n▫️Когда: {dt_str}\n▫️Имя: {user_name}\n▫️Телефон: "
                     f"{phone}\n▫️Комментарий: {comment}")
        admin_text = (f"❕ Напоминание о записи (мастеру)!🕰\n▫️ID записи: #{appt_id}\n▫️{translated_service}\n▫️Когда: "
                      f"{dt_str}\n▫️Клиент: {user_name}\n▫️Телефон: {phone}\n▫️Комментарий: {comment}")

        try:
            await bot_tests.send_message(user_id, user_text)
        except Exception:
            logging.exception("Не удалось отправить напоминание клиенту")

        try:
            await bot_tests.send_message(ADMIN_ID, admin_text)
        except Exception:
            logging.exception("Не удалось отправить напоминание администратору")

    except asyncio.CancelledError:
        return
    except Exception:
        logging.exception("Ошибка в reminder_worker")
    finally:
        GLOBAL_REMINDER_TASKS.pop(appt_id, None)


def schedule_reminder(appt_id: int, appt_dt: datetime):
    global GLOBAL_LOOP
    if GLOBAL_LOOP is None:
        GLOBAL_LOOP = asyncio.get_event_loop()  # Инициализируем, если еще не инициализирован

    existing = GLOBAL_REMINDER_TASKS.get(appt_id)
    if existing:
        try:
            existing.cancel()
        except Exception:
            pass
    task = GLOBAL_LOOP.create_task(reminder_worker(appt_id, appt_dt))
    GLOBAL_REMINDER_TASKS[appt_id] = task


@dp.callback_query_handler(lambda c: c.data and c.data.startswith("sign_up_"), state="*")
async def handle_sign_up(call: types.CallbackQuery, state: FSMContext):
    global last_message_id  # Объявляем переменную как глобальную
    # Удаляем предыдущее сообщение, если оно существует
    if last_message_id:
        try:
            await bot_tests.delete_message(chat_id=call.message.chat.id, message_id=last_message_id)
        except Exception as e:
            logging.error(f"Ошибка при удалении сообщения: {e}")
    await call.answer()

    # ИЗМЕНЕНИЕ: Извлекаем технический ключ услуги и получаем русское название из SERVICES_MAP
    service_key = call.data.replace("sign_up_", "")
    # Сохраняем в state (и затем в БД) именно технический ключ, а не переведенное название.
    # Перевод будет происходить при извлечении из БД.
    await state.update_data(service=service_key)

    # Для отображения пользователю сразу переводим
    service_russian_name = SERVICES_MAP.get(service_key,
                                            service_key.replace("_", " ").capitalize())  # Fallback для отображения

    now = datetime.now(tz)
    cal_kb = create_calendar(now.year, now.month, now.year, now.month)
    with open('photo_calendar.jpg', 'rb') as img:
        new_message = await call.message.answer_photo(img,
                                                      f"▫️Вы выбрали услугу: {service_russian_name}. 💅🏼\n\n▫️Выберите, пожалуйста, нужную вам дату: 👇🏼 ",
                                                      reply_markup=cal_kb)
    last_message_id = new_message.message_id  # Сохраняем ID нового сообщения
    await call.answer()


@dp.callback_query_handler(text="BACK_TO_CALENDAR", state="*")
async def back_to_calendar(call: types.CallbackQuery, state: FSMContext):
    # Логика возврата: просто вызываем заново функцию выбора даты
    data = await state.get_data()
    service_key_from_state = data.get("service", "услугу")  # Получаем технический ключ из state
    # ИЗМЕНЕНИЕ: Переводим название услуги для отображения
    service_russian_name = SERVICES_MAP.get(service_key_from_state,
                                            service_key_from_state.replace("_", " ").capitalize())

    global last_message_id
    if last_message_id:
        try:
            await bot_tests.delete_message(chat_id=call.message.chat.id, message_id=last_message_id)
        except Exception:
            pass
    now = datetime.now(tz)
    cal_kb = create_calendar(now.year, now.month, now.year, now.month)
    with open('photo_calendar.jpg', 'rb') as img:
        new_message = await call.message.answer_photo(img,
                                                      f"▫️Вы выбрали услугу: {service_russian_name}. 💅🏼\n\n▫️Выберите, пожалуйста, нужную вам дату: 👇🏼 ",
                                                      reply_markup=cal_kb)
    last_message_id = new_message.message_id
    await call.answer()


@dp.callback_query_handler(lambda c: c.data and c.data.startswith("CAL|"))
async def cal_nav(callback: types.CallbackQuery):
    await callback.answer()
    payload = callback.data.split("|", 1)[1]
    year, month = map(int, payload.split("-"))
    now = datetime.now(tz)
    cal = create_calendar(year, month, now.year, now.month)
    try:
        await callback.message.edit_reply_markup(cal)
    except MessageNotModified:  # aiogram.utils.exceptions.MessageNotModified
        pass  # Игнорируем, если клавиатура не изменилась
    except Exception:
        await callback.message.answer("▫️Выберите, пожалуйста, нужную вам дату: 👇🏼", reply_markup=cal)


@dp.callback_query_handler(lambda c: c.data and c.data.startswith("DATE|"))
async def handle_date_select(call: types.CallbackQuery):
    global last_message_id  # Объявляем переменную как глобальную
    # Удаляем предыдущее сообщение, если оно существует
    if last_message_id:
        try:
            await bot_tests.delete_message(chat_id=call.message.chat.id, message_id=last_message_id)
        except Exception as e:
            logging.error(f"Ошибка при удалении сообщения: {e}")
    await call.answer()
    date_str = call.data.split("|", 1)[1]
    kb = times_kb_for_date(date_str)
    with open('photo_time.jpg', 'rb') as img:
        new_message = await call.message.answer_photo(img,
                                                      f"▫️Вы выбрали дату: {date_str}.\n\n▫️Выберите, пожалуйста, нужное вам время (❌ - время уже занято): 👇🏼",
                                                      reply_markup=kb)
    last_message_id = new_message.message_id  # Сохраняем ID нового сообщения
    await call.answer()


@dp.callback_query_handler(lambda c: c.data and c.data.startswith("TIME|"))
async def handle_time_select(call: types.CallbackQuery, state: FSMContext):
    global last_message_id  # Объявляем переменную как глобальную
    # Удаляем предыдущее сообщение, если оно существует
    if last_message_id:
        try:
            await bot_tests.delete_message(chat_id=call.message.chat.id, message_id=last_message_id)
        except Exception as e:
            logging.error(f"Ошибка при удалении сообщения: {e}")
    await call.answer()

    _, date_str, time_str = call.data.split("|")
    appt_dt = parse_dt_local(date_str, time_str)
    dt_str = appt_dt.strftime("%Y-%m-%d %H:%M")

    # Проверяем свободен ли слот
    if not is_slot_free(dt_str):
        # Если слот занят, формируем клавиатуру для выбора свободного времени
        kb = times_kb_for_date(date_str)
        with open('photo_time.jpg', 'rb') as img:
            new_message = await call.message.answer_photo(img,
                                                          "▫️К сожалению, этот слот уже занят. 😞\n\n▫️Выберите, пожалуйста, другой свободный слот (❌ - время уже занято): 👇🏼",
                                                          reply_markup=kb)
        last_message_id = new_message.message_id  # Сохраняем ID нового сообщения
        return

    # Если слот свободен, продолжаем процесс бронирования
    await state.update_data(chosen_date=date_str, chosen_time=time_str)
    kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    with open('photo_your_name.jpg', 'rb') as img:
        new_message = await call.message.answer_photo(img,
                                                      f"▫️Вы выбрали следующую дату и время: {dt_str}.\n\n▫️Введите, пожалуйста, ваше имя: 👇🏼",
                                                      reply_markup=kb)
    last_message_id = new_message.message_id  # Сохраняем ID нового сообщения
    await BookingStates.waiting_name.set()
    await call.answer()


@dp.message_handler(state=BookingStates.waiting_name,
                    content_types=[types.ContentType.TEXT])
async def process_name(message: types.Message, state: FSMContext):
    global last_message_id  # Объявляем переменную как глобальную
    # Удаляем предыдущее сообщение, если оно существует
    if last_message_id:
        try:
            await bot_tests.delete_message(chat_id=message.chat.id, message_id=last_message_id)
        except Exception as e:
            logging.error(f"Ошибка при удалении сообщения: {e}")

    await state.update_data(user_name=message.text.strip())
    kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    kb.add(KeyboardButton("Отправить номер", request_contact=True))
    kb.add(KeyboardButton("Ввести номер вручную"))
    with open('photo_your_number.jpg', 'rb') as img:
        new_message = await message.answer_photo(img,
                                                 "▫️Отправьте, пожалуйста, свой номер телефона для записи на услугу или введите свой номер телефона вручную, нажав на одну из кнопок ниже: 👇🏼",
                                                 reply_markup=kb)
    last_message_id = new_message.message_id
    await BookingStates.waiting_phone.set()


@dp.message_handler(content_types=[types.ContentType.CONTACT],
                    state=BookingStates.waiting_phone)
async def process_phone_contact(message: types.Message, state: FSMContext):
    global last_message_id  # Объявляем переменную как глобальную
    # Удаляем предыдущее сообщение, если оно существует
    if last_message_id:
        try:
            await bot_tests.delete_message(chat_id=message.chat.id, message_id=last_message_id)
        except Exception as e:
            logging.error(f"Ошибка при удалении сообщения: {e}")

    phone = message.contact.phone_number
    await state.update_data(phone=phone)
    with open('photo_your_comm.jpg', 'rb') as img:
        new_message = await message.answer_photo(img, "▫️Оставьте, пожалуйста, свой комментарий для записи (ваши какие-либо пожелания или предупреждения). 👐🏻 \n"
                                                      "\n▫️Если комментария нет, то напишите, пожалуйста, слово 'Нет': 👇🏼",
                                                 reply_markup=ReplyKeyboardMarkup(resize_keyboard=True,
                                                                                  one_time_keyboard=True))
    last_message_id = new_message.message_id  # Сохраняем ID нового сообщения
    await BookingStates.waiting_comment.set()


@dp.message_handler(lambda m: m.text == "Ввести номер вручную",
                    state=BookingStates.waiting_phone)
async def ask_manual_phone(message: types.Message):
    global last_message_id  # Объявляем переменную как глобальную
    # Удаляем предыдущее сообщение, если оно существует
    if last_message_id:
        try:
            await bot_tests.delete_message(chat_id=message.chat.id, message_id=last_message_id)
        except Exception as e:
            logging.error(f"Ошибка при удалении сообщения: {e}")

    with open('photo_your_number.jpg', 'rb') as img:
        new_message = await message.answer_photo(img, "▫️Введите, пожалуйста, свой номер телефона в следующем формате ниже (без кавычек): 👇🏼\n\n▫️Пример: '+71234567890'")
    last_message_id = new_message.message_id  # Сохраняем ID нового сообщения


@dp.message_handler(state=BookingStates.waiting_phone,
                    content_types=[types.ContentType.TEXT])
async def process_phone_manual(message: types.Message, state: FSMContext):
    global last_message_id  # Объявляем переменную как глобальную
    # Удаляем предыдущее сообщение, если оно существует
    if last_message_id:
        try:
            await bot_tests.delete_message(chat_id=message.chat.id, message_id=last_message_id)
        except Exception as e:
            logging.error(f"Ошибка при удалении сообщения: {e}")

    text = message.text.strip()
    if not PHONE_RE.match(text):
        with open('photo_your_number.jpg', 'rb') as img:
            new_message = await message.answer_photo(img, "▫️Неверный формат номера! Попробуйте, пожалуйста, ввести свой номер телефона ещё раз (без кавычек): 👇🏼\n"
                                                          "\n▫️Пример: '+71234567890'")
        last_message_id = new_message.message_id  # Сохраняем ID нового сообщения
        return

    await state.update_data(phone=text)
    with open('photo_your_comm.jpg', 'rb') as img:
        new_message = await message.answer_photo(img, "▫️Оставьте, пожалуйста, свой комментарий для записи (ваши какие-либо пожелания или предупреждения). 👐🏻\n"
                                                      "\n▫️Если комментария нет, то напишите, пожалуйста, слово 'Нет': 👇🏼",
                                                 reply_markup=ReplyKeyboardMarkup(resize_keyboard=True,
                                                                                  one_time_keyboard=True))
    last_message_id = new_message.message_id  # Сохраняем ID нового сообщения
    await BookingStates.waiting_comment.set()


@dp.message_handler(state=BookingStates.waiting_comment,
                    content_types=[types.ContentType.TEXT])
async def process_comment(message: types.Message, state: FSMContext):
    global last_message_id  # Объявляем переменную как глобальную
    # Удаляем предыдущее сообщение, если оно существует
    if last_message_id:
        try:
            await bot_tests.delete_message(chat_id=message.chat.id, message_id=last_message_id)
        except Exception as e:
            logging.error(f"Ошибка при удалении сообщения: {e}")

    await state.update_data(comment=message.text.strip())
    await state.update_data(pd_consent=False, mail_consent=False)
    new_message = await message.answer("▫️Для успешного подтверждения записи на выбранную вами услугу, вам необходимо дать согласия на следующие пункты: 👇🏼\n\n1. Согласие на обработку персональных данных (ваш номер телефона,  ваше имя).\n2. Согласие на отправку вам новых сообщений через нашего бота.\n\n▫️Чтобы дать согласие - нажмите на кнопки ниже: 👇🏼",
                                       reply_markup=consents_kb(False, False))
    last_message_id = new_message.message_id  # Сохраняем ID нового сообщения
    await BookingStates.waiting_consents.set()


@dp.callback_query_handler(lambda c: c.data in ("TOGGLE_PD", "TOGGLE_MAIL", "SUBMIT"),
                           state=BookingStates.waiting_consents)
async def handle_consents(call: types.CallbackQuery, state: FSMContext):
    await call.answer()

    # TOGGLE_PD
    if call.data == "TOGGLE_PD":
        data = await state.get_data()
        pd = not data.get("pd_consent", False)
        mail = data.get("mail_consent", False)
        await state.update_data(pd_consent=pd)
        try:
            await call.message.edit_text(
                "▫️Для успешного подтверждения записи на выбранную вами услугу, вам необходимо дать согласия на следующие пункты: 👇🏼\n\n1. Согласие на обработку персональных данных (ваш номер телефона,  ваше имя).\n2. Согласие на отправку вам новых сообщений через нашего бота.\n\n▫️Чтобы дать согласие нажмите на кнопки ниже: 👇🏼",
                reply_markup=consents_kb(pd, mail)
            )
        except MessageNotModified:
            pass
        except Exception:
            logging.exception("Не удалось обновить сообщение при TOGGLE_PD")
        return

    # TOGGLE_MAIL
    if call.data == "TOGGLE_MAIL":
        data = await state.get_data()
        pd = data.get("pd_consent", False)
        mail = not data.get("mail_consent", False)
        await state.update_data(mail_consent=mail)
        try:
            await call.message.edit_text(
                "▫️Для успешного подтверждения записи на выбранную вами услугу, вам необходимо дать согласия на следующие пункты: 👇🏼\n\n1. Согласие на обработку персональных данных (ваш номер телефона,  ваше имя).\n2. Согласие на отправку вам новых сообщений через нашего бота.\n\n▫️Чтобы дать согласие нажмите на кнопки ниже: 👇🏼",
                reply_markup=consents_kb(pd, mail)
            )
        except MessageNotModified:
            pass
        except Exception:
            logging.exception("Не удалось обновить сообщение при TOGGLE_MAIL")
        return

    # SUBMIT
    if call.data == "SUBMIT":
        # Берём актуальные значения из state
        data = await state.get_data()
        pd = data.get("pd_consent", False)
        mail = data.get("mail_consent", False)

        if not pd or not mail:
            await call.answer("▫️Для того, чтобы записаться на выбранную вами услугу, необходимо дать оба согласия (для подтверждения согласия нажмите на кнопки ниже): 👇🏼", show_alert=True)
            return

        # Попытка удалить сообщение не критично
        try:
            await bot_tests.delete_message(chat_id=call.message.chat.id,
                                           message_id=call.message.message_id)
        except Exception:
            pass

        # Получаем данные брони
        st = await state.get_data()
        user_id = call.from_user.id
        service_key_from_state = st.get("service", "услугу")  # Получаем технический ключ
        # ИЗМЕНЕНИЕ: Переводим название услуги для использования в сообщении и БД
        service_russian_name = SERVICES_MAP.get(service_key_from_state,
                                                service_key_from_state.replace("_", " ").capitalize())

        name = st.get("user_name")
        phone = st.get("phone")
        comment = st.get("comment")
        date_str = st.get("chosen_date")
        time_str = st.get("chosen_time")

        try:
            appt_dt = parse_dt_local(date_str, time_str)
        except Exception:
            try:
                await bot_tests.send_message(user_id, "▫️Ошибка с датой/временем записи! Попробуйте, пожалуйста, заново.")
            except Exception:
                logging.exception("Не удалось уведомить клиента об ошибке даты!")
            await state.finish()
            return

        dt_str = appt_dt.strftime("%Y-%m-%d %H:%M")

        # Проверка свободного слота
        if not is_slot_free(dt_str):
            try:
                await bot_tests.send_message(user_id, f"▫️К сожалению, выбранный вами слот {dt_str} заняли в момент подтверждения записи. 😞\n\n▫️Попробуйте, пожалуйста, выбрать другой свободный слот.")
            except Exception:
                logging.exception("Не удалось уведомить клиента о занятости слота!")
            await state.finish()
            return

        created = datetime.now(tz).isoformat()
        try:
            cur_appt.execute(
                "INSERT INTO appointments (user_id, service, user_name, phone, comment, datetime,\n"
                "created_at) VALUES (?,?,?,?,?,?,?)",
                (user_id, service_key_from_state, name, phone, comment, dt_str, created)
                # Сохраняем технический ключ в БД
            )
            conn_appt.commit()
        except sqlite3.IntegrityError:
            # гонка — слот заняли
            try:
                await bot_tests.send_message(user_id, "▫️К сожалению, выбранный вами слот в момент подтверждения записи заняли. 😞\n\n▫️Попробуйте, пожалуйста, выбрать другой свободный слот.")
            except Exception:
                logging.exception("Не удалось уведомить клиента об IntegrityError!")
            await state.finish()
            return
        except Exception:
            logging.exception("Ошибка при вставке записи в БД")
            try:
                await bot_tests.send_message(user_id, "▫️К сожалению, произошла ошибка при создании записи! 😞\n\n"
                                                      "▫️Попробуйте, пожалуйста, ещё раз позже.")
            except Exception:
                pass
            await state.finish()
            return

        appt_id = cur_appt.lastrowid

        # Уведомление админа
        try:
            await bot_tests.send_message(ADMIN_ID, f"❕ У вас новая запись!\n▫️ ID записи: #{appt_id}\n▫️Услуга: "
                                                   f"{service_russian_name}\n▫️Когда: {dt_str}\n▫️Клиент: {name}\n▫️Телефон: {phone}\n▫️Комментарий: {comment}")
        except Exception:
            logging.exception("Не удалось уведомить администратора!")

        # Подтверждение пользователю
        try:
            await bot_tests.send_message(user_id, f"❕ Ваша запись успешно подтверждена!\n▫️ID записи: "
                                                  f"{appt_id}\n▫️Услуга: {service_russian_name}\n▫️Когда: {dt_str}\n▫️Имя: {name}\n▫️Телефон: {phone}")
            await bot_tests.send_message(user_id, "❕ Готово! Напоминание о записи придёт за 2 часа до её начала. 🕰", reply_markup=registration_back_menu_kb)
        except Exception:
            logging.exception("Не удалось отправить подтверждение клиенту!")

        # Планируем напоминание
        try:
            schedule_reminder(appt_id, appt_dt)
        except Exception:
            logging.exception("Не удалось запланировать напоминание!")

        await state.finish()


@dp.callback_query_handler(lambda c: c.data == "IGNORE")
async def ignore_cb(call: types.CallbackQuery):
    await call.answer()


async def _send_my_appointments_list(message: types.Message):
    # uid = message.from_user.id # ИЗМЕНЕНИЕ: Этот uid больше не нужен для фильтрации всех записей
    today_start_str = datetime.now(tz).strftime("%Y-%m-%d 00:00")  # Начало текущего дня для сравнения

    # --- Логика автоматического удаления старых записей ---
    try:
        # ИЗМЕНЕНИЕ: Удаляем фильтрацию по user_id для удаления всех старых записей
        cur_appt.execute("SELECT id, datetime FROM appointments WHERE datetime < ?",
                         (today_start_str,))
        past_appts = cur_appt.fetchall()

        if past_appts:
            deleted_ids = [appt[0] for appt in past_appts]
            # Удаляем записи из базы данных
            cur_appt.execute(f"DELETE FROM appointments WHERE id IN ({','.join(map(str, deleted_ids))})")
            conn_appt.commit()
            logging.info(f"Удалены прошедшие записи: {deleted_ids}")  # ИЗМЕНЕНИЕ: Убрал user_id из лога

            # Отменяем напоминания для удаленных записей
            for appt_id in deleted_ids:
                task = GLOBAL_REMINDER_TASKS.pop(appt_id, None)
                if task:
                    try:
                        task.cancel()
                    except Exception:
                        logging.exception(f"Ошибка при отмене задачи напоминания для удаленной записи {appt_id}")

    except Exception as e:
        logging.error(f"Ошибка при автоматическом удалении старых записей: {e}")  # ИЗМЕНЕНИЕ: Убрал user_id из лога
        # Продолжаем выполнение, чтобы показать оставшиеся записи, даже если удаление не удалось

    # --- Оригинальная логика отображения текущих записей ---
    try:
        # ИЗМЕНЕНИЕ: Убираем фильтрацию по user_id для отображения всех записей
        cur_appt.execute("SELECT id, service, datetime, user_name, phone FROM appointments ORDER BY datetime")
        rows = cur_appt.fetchall()
    except Exception:
        logging.exception("Ошибка чтения БД в _send_my_appointments_list (после удаления)")
        await message.reply("▫️Ошибка при получении записей! Попробуйте, пожалуйста, позже.")
        return

    if not rows:
        await message.reply("▫️К сожалению, у вас еще нет записей. 😞",
                            reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add("Главное меню"))
        return

    text_lines = []
    for index, r in enumerate(rows):
        aid, service_db, dt_str, user_name, phone = r

        # ИЗМЕНЕНИЕ: Нормализуем ключ и переводим название услуги на русский язык перед форматированием
        normalized_service_key = service_db.lower().replace(" ", "_")
        translated_service = SERVICES_MAP.get(normalized_service_key, service_db)  # Fallback, если ключ не найден

        # Форматируем вывод в соответствии с запрошенной структурой
        appointment_text = (
            f"❕ {index + 1}.\n"
            f"   ▫️ID записи: {aid}\n"
            f"   ▫️Услуга: {translated_service}\n"
            f"   ▫️Дата и время: {dt_str}\n"
            f"   ▫️Имя: {user_name}\n"
            f"   ▫️Телефон: {phone}"
        )
        text_lines.append(appointment_text)

    # Используем двойной перенос строки для лучшего разделения записей
    kb_for_my_appointments = ReplyKeyboardMarkup(resize_keyboard=True)
    kb_for_my_appointments.add("Отменить запись")
    kb_for_my_appointments.add("Главное меню")
    await message.reply("\n\n".join(text_lines), reply_markup=kb_for_my_appointments)


# Обработчик для кнопки "Мои записи" в админ-панели
@dp.message_handler(lambda message: message.text == "Мои записи")
async def admin_my_appointments_button(message: types.Message):
    # Проверка на ADMIN_ID уже есть в cmd_admin, но для надежности можно добавить и здесь,
    # если эта кнопка может быть доступна не только через админ-панель.
    # В данном случае, поскольку она добавляется в админ-панель, предполагается,
    # что только админ может ее нажать.
    if message.from_user.id != ADMIN_ID: # Добавил проверку на админа
        await message.reply("К сожалению, у вас нет доступа к этой функции! 😞")
        return
    await _send_my_appointments_list(message) # Вызываем основную логику


# Новый обработчик для кнопки "Отменить запись"
@dp.message_handler(lambda message: message.text == "Отменить запись", state="*")
async def request_cancel_appointment_id(message: types.Message, state: FSMContext):
    # Проверяем, что это админ
    if message.from_user.id != ADMIN_ID:
        await message.reply("К сожалению, у вас нет доступа к этой функции! 😞")
        return

    await AdminStates.waiting_for_appointment_id_to_cancel.set()

    # Получаем список записей, чтобы показать их пользователю
    # ИЗМЕНЕНИЕ: Здесь также убираем фильтрацию по user_id, чтобы админ видел все записи для отмены
    # uid = message.from_user.id # Больше не нужен
    today_start_str = datetime.now(tz).strftime("%Y-%m-%d 00:00")

    try:
        # ИЗМЕНЕНИЕ: Удаляем фильтрацию по user_id для удаления всех старых записей
        cur_appt.execute("SELECT id, datetime FROM appointments WHERE datetime < ?",
                         (today_start_str,))
        past_appts = cur_appt.fetchall()

        if past_appts:
            deleted_ids = [appt[0] for appt in past_appts]
            cur_appt.execute(f"DELETE FROM appointments WHERE id IN ({','.join(map(str, deleted_ids))})")
            conn_appt.commit()
            logging.info(f"Удалены прошедшие записи (перед отменой): {deleted_ids}")

            for appt_id in deleted_ids:
                task = GLOBAL_REMINDER_TASKS.pop(appt_id, None)
                if task:
                    try:
                        task.cancel()
                    except Exception:
                        logging.exception(f"Ошибка при отмене задачи напоминания для удаленной записи {appt_id}")

    except Exception as e:
        logging.error(f"Ошибка при автоматическом удалении старых записей (перед отменой): {e}")

    try:
        # ИЗМЕНЕНИЕ: Убираем фильтрацию по user_id для отображения всех записей
        cur_appt.execute("SELECT id, service, datetime, user_name, phone FROM appointments ORDER BY datetime", )
        rows = cur_appt.fetchall()
    except Exception:
        logging.exception("Ошибка чтения БД при запросе отмены")
        await message.reply("▫️Ошибка при получении записей для отмены! Попробуйте, пожалуйста, позже.",
                            reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add("Главное меню"))
        await state.finish()
        return

    if not rows:
        await message.reply("К сожалению, у вас нет активных записей для отмены. 😞",
                            reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add("Главное меню"))
        await state.finish()
        return

    text_lines = ["▫️Введите, пожалуйста, ID записи, которую хотите отменить (или несколько ID через запятую): 👇🏼"]
    for index, r in enumerate(rows):
        aid, service_db, dt_str, user_name, phone = r
        # ИЗМЕНЕНИЕ: Нормализуем ключ и переводим название услуги на русский язык перед форматированием
        normalized_service_key = service_db.lower().replace(" ", "_")
        translated_service = SERVICES_MAP.get(normalized_service_key, service_db)
        appointment_text = (
            f"❕ {index + 1}.\n"
            f"   ▫️ID записи: {aid}\n"
            f"   ▫️Услуга: {translated_service}\n"
            f"   ▫️Дата и время: {dt_str}\n"
            f"   ▫️Имя: {user_name}\n"
            f"   ▫️Телефон: {phone}"
        )
        text_lines.append(appointment_text)

    await message.reply("\n\n".join(text_lines),
                        reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add("Главное меню"))


# Обработчик для ввода ID записи для отмены
@dp.message_handler(state=AdminStates.waiting_for_appointment_id_to_cancel,
                    content_types=[types.ContentType.TEXT])
async def process_cancel_appointment_id(message: types.Message, state: FSMContext):
    ids_to_cancel_str = message.text.strip()

    # Проверяем, что введены только цифры и запятые
    if not re.fullmatch(r'[\d, ]+', ids_to_cancel_str):
        await message.reply(
            "▫️Неверный формат ввода! Пожалуйста, введите ID записи (число) или несколько ID через запятую: 👇🏼")
        return

    ids_to_cancel = [int(id_str.strip()) for id_str in ids_to_cancel_str.split(',') if id_str.strip().isdigit()]

    if not ids_to_cancel:
        await message.reply("К сожалению, не было введено ни одного валидного ID записи. 😞")
        await state.finish()
        return

    deleted_count = 0
    failed_ids = []

    for aid in ids_to_cancel:
        try:
            # Проверяем, существует ли запись и принадлежит ли она пользователю или админу
            cur_appt.execute("SELECT user_id, service, datetime FROM appointments WHERE id=?", (aid,))
            row = cur_appt.fetchone()

            if not row:
                failed_ids.append(str(aid))
                continue

            owner_id, service_db, dt_str = row
            # ИЗМЕНЕНИЕ: Нормализуем ключ и переводим название услуги на русский язык перед использованием в сообщении
            normalized_service_key = service_db.lower().replace(" ", "_")
            translated_service = SERVICES_MAP.get(normalized_service_key, service_db)

            # ИЗМЕНЕНИЕ: Проверка прав теперь должна быть только для ADMIN_ID, так как это админ-функция
            # if message.from_user.id != owner_id and message.from_user.id != ADMIN_ID:
            #     failed_ids.append(f"{aid} (нет прав)")
            #     continue
            # Поскольку это функция админа, предполагаем, что админ имеет право отменять любую запись.
            # Если админ пытается отменить запись, которую он сам не делал, это нормально.
            # Если же вы хотите, чтобы админ мог отменять только свои записи, то оставьте проверку.
            # Но по запросу "админ видит все записи", логично, что он может отменять все.
            if message.from_user.id != ADMIN_ID:  # Дополнительная проверка, хотя состояние уже для админа
                failed_ids.append(f"{aid} (нет прав администратора)")
                continue

            # Удаляем запись
            cur_appt.execute("DELETE FROM appointments WHERE id=?", (aid,))
            conn_appt.commit()
            deleted_count += 1
            logging.info(f"Запись #{aid} отменена администратором {message.from_user.id}")  # ИЗМЕНЕНИЕ: Уточнил лог

            # Отменяем напоминание
            task = GLOBAL_REMINDER_TASKS.pop(aid, None)
            if task:
                try:
                    task.cancel()
                    logging.info(f"Задача напоминания для записи #{aid} отменена.")
                except Exception:
                    logging.exception(f"Ошибка при отмене задачи напоминания для удаленной записи {aid}")

            # Уведомления (не критично)
            try:
                await bot_tests.send_message(owner_id,
                                             f"❕ Ваша запись была отменена администратором!\n\n▫️В скором времени администратор свяжется с вами, приносим свои извинения за неудобство.\n\n▫️ID записи: #{aid}\n▫️Услуга: {translated_service}\n▫️Дата и время: {dt_str}")
            except Exception:
                logging.exception("Не удалось отправить сообщение клиенту об отмене")
            try:
                await bot_tests.send_message(ADMIN_ID, f"❕ Запись успешно была отменена!\n▫️ID записи: #{aid}\n▫️Услуга: {translated_service}\n▫️Дата и время: {dt_str}")
            except Exception:
                logging.exception("Не удалось отправить сообщение админу об отмене")

        except Exception as e:
            logging.exception(f"Ошибка при обработке отмены записи ID {aid}: {e}")
            failed_ids.append(str(aid))

    response_message = f"Результат отмены записей:\n"
    if deleted_count > 0:
        response_message += f"▫️Успешно отменено: {deleted_count}\n"
    if failed_ids:
        response_message += f"▫️Не удалось отменить (ID или нет прав): {', '.join(failed_ids)}\n"

    await message.reply(response_message, reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add("Главное меню"))
    await state.finish()


LAST_MESSAGE_BY_CHAT: dict[int, int] = {} # Перемещено сюда, чтобы быть ближе к обработчику


@dp.message_handler(
    lambda m: m.text and m.chat.type == 'private' and not any(e.type == 'bot_command' for e in (m.entities or [])),
    content_types=types.ContentType.TEXT,
    state='*'
)
async def handle_user_message(message: types.Message):
    chat_id = message.chat.id

    # удаляем предыдущее бот-сообщение в этом чате (если есть)
    prev_id = LAST_MESSAGE_BY_CHAT.get(chat_id)
    if prev_id:
        try:
            await bot_tests.delete_message(chat_id=chat_id, message_id=prev_id)
        except Exception:
            pass

    # безопаснее использовать full_name, username может быть None
    user_ident = message.from_user.username or message.from_user.full_name or \
                 str(message.from_user.id)
    try:
        await bot_tests.send_message(ADMIN_ID, f"▫️Пользователь {user_ident} "
                                               f"({message.from_user.id}) написал вам сообщение: 👇🏼\n\n{message.text}")
        new_message = await message.reply("▫️Ваше сообщение было успешно отправлено администратору! 🤗",
                                          reply_markup=consultation_back_menu_kb)
        LAST_MESSAGE_BY_CHAT[chat_id] = new_message.message_id
    except Exception:
        logging.exception("Ошибка пересылки админу")


async def on_startup(dp):
    global GLOBAL_LOOP
    GLOBAL_LOOP = asyncio.get_event_loop()
    try:
        cur_appt.execute("SELECT id, datetime FROM appointments")
        rows = cur_appt.fetchall()
        for aid, dt_str in rows:
            try:
                appt_dt = tz.localize(datetime.strptime(dt_str, "%Y-%m-%d %H:%M"))
            except Exception:
                continue
            remind_at = appt_dt - timedelta(hours=2)
            if remind_at > datetime.now(tz):
                schedule_reminder(aid, appt_dt)
    except Exception:
        logging.exception("Ошибка при восстановлении напоминаний")


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
