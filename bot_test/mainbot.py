from aiogram import Bot, Dispatcher, executor, types
from aiogram.utils import executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.dispatcher import filters
from bot_test.config import *
from bot_test.keyboards import *
import bot_test.texsts
import logging

logging.basicConfig(level=logging.INFO)

bot_tests = Bot(token=api)
dp = Dispatcher(bot_tests, storage=MemoryStorage())

# ID администратора (ваш Telegram ID)
ADMIN_ID = 1060502535  # Замените на ваш ID

# Список зарегистрированных пользователей (пример)
registered_users = {}

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    user_id = message.from_user.id
    phone_number = message.contact.phone_number if message.contact else "Не указано"
    name = message.from_user.full_name
    custom_name = message.from_user.username

    # Регистрируем пользователя
    registered_users[user_id] = {
        'name': name,
        'phone': phone_number,
        'custom_name': custom_name,
    }
    with open('photo_1.jpg', 'rb') as img:
        await message.answer_photo(img, f'Добро пожаловать, {message.from_user.full_name}!👋\n' + bot_test.texsts.start_text, parse_mode=types.ParseMode.HTML, reply_markup=start_kb)

class AdminStates(StatesGroup):
    waiting_for_users_selection = State()
    waiting_for_message = State()
    waiting_for_media = State()
    waiting_for_user_ids_to_send_message = State()
    waiting_for_user_id_to_delete = State()
    waiting_for_new_name = State()

# Команда /admin
@dp.message_handler(commands=['admin'])
async def cmd_admin(message: types.Message):
    if message.from_user.id == ADMIN_ID:
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add("Список пользователей", "Отправить сообщение выбранным пользователям", "Отправить всем сообщение",
                 "Удалить пользователя")
        await message.answer(f"Добро пожаловать в панель администратора {message.from_user.username}", reply_markup=keyboard)
    else:
        await message.answer("У вас нет доступа к админ-панели!")


# Обработка кнопок админ-панели
@dp.message_handler(lambda message: message.text == "Список пользователей")
async def list_users(message: types.Message):
    if not registered_users:
        await message.reply("Нет зарегистрированных пользователей.")
        return

    user_list = "\n".join(
        [f"ID: {user_id}, Имя: {user['name']}, Имя пользователя (через @): {user.get('custom_name', 'Не указано')}" for user_id, user in registered_users.items()])
    await message.reply(f"Список зарегистрированных пользователей:\n{user_list}")

@dp.message_handler(lambda message: message.text == "Отправить сообщение выбранным пользователям")
async def select_users_to_send_message(message: types.Message, state: FSMContext):
    await AdminStates.waiting_for_users_selection.set()

    if not registered_users:
        await message.reply("Нет зарегистрированных пользователей.")
        await state.finish()
        return

    user_list = "\n".join([f"ID: {user_id}, Имя: {user['name']}, Имя пользователя (через @): {user.get('custom_name', 'Не указано')}" for user_id, user in registered_users.items()])
    await message.reply(f"Выберите пользователей по ID (через запятую), которым хотите отправить сообщение:\n{user_list}")


@dp.message_handler(state=AdminStates.waiting_for_users_selection)
async def get_selected_users(message: types.Message, state: FSMContext):
    user_ids = message.text.split(", ")
    valid_user_ids = []

    for user_id in user_ids:
        user_id = user_id.strip()
        if user_id.isdigit() and int(user_id) in registered_users:
            valid_user_ids.append(int(user_id))

    if valid_user_ids:
        await state.update_data(valid_user_ids=valid_user_ids)
        await AdminStates.waiting_for_media.set()
        await message.reply("Введите сообщение для выбранных пользователей:")
    else:
        await message.reply("Нет валидных ID пользователей. Попробуйте снова.")
        await state.finish()


@dp.message_handler(state=AdminStates.waiting_for_media, content_types=types.ContentTypes.ANY)
async def process_message_to_selected(message: types.Message, state: FSMContext):
    data = await state.get_data()
    valid_user_ids = data.get('valid_user_ids', [])

    if valid_user_ids:
        for user_id in valid_user_ids:
            try:
                if message.content_type == 'text':
                    await bot_tests.send_message(user_id, message.text)
                elif message.content_type == 'photo':
                    await bot_tests.send_photo(user_id, message.photo[-1].file_id, caption=message.caption)
                elif message.content_type == 'video':
                    await bot_tests.send_video(user_id, message.video.file_id, caption=message.caption)
                elif message.content_type == 'audio':
                    await bot_tests.send_audio(user_id, message.audio.file_id, caption=message.caption)
                elif message.content_type == 'voice':
                    await bot_tests.send_voice(user_id, message.voice.file_id, caption=message.caption)
                elif message.content_type == 'sticker':  # Обработка стикеров
                    await bot_tests.send_sticker(user_id, message.sticker.file_id)  # Отправка стикера
                elif message.content_type == 'video_note':  # Обработка видео-сообщений
                    await bot_tests.send_video_note(user_id, message.video_note.file_id)  # Отправка видео-сообщения
                elif message.content_type == 'document':  # Обработка документов
                    await bot_tests.send_document(user_id, message.document.file_id, caption=message.caption) #Отправка документа
            except Exception as e:
                await message.reply(f"Не удалось отправить сообщение выбранным пользователям {user_id}: {e}")

        await message.reply("Сообщение отправлено выбранным пользователям.")
    else:
        await message.reply("Не было выбрано ни одного пользователя для отправки сообщения.")
    await state.finish()

@dp.message_handler(lambda message: message.text == "Отправить всем сообщение")
async def send_message_to_all(message: types.Message):
    await AdminStates.waiting_for_message.set()
    await message.reply("Введите сообщение для всех зарегистрированных пользователей:")


@dp.message_handler(state=AdminStates.waiting_for_message, content_types=types.ContentTypes.ANY)
async def process_message_to_all(message: types.Message, state: FSMContext):
    for user_id in registered_users.keys():
        try:
            if message.content_type == 'text':
                await bot_tests.send_message(user_id, message.text)
            elif message.content_type == 'photo':
                await bot_tests.send_photo(user_id, message.photo[-1].file_id, caption=message.caption)
            elif message.content_type == 'video':
                await bot_tests.send_video(user_id, message.video.file_id, caption=message.caption)
            elif message.content_type == 'audio':
                await bot_tests.send_audio(user_id, message.audio.file_id, caption=message.caption)
            elif message.content_type == 'voice':
                await bot_tests.send_voice(user_id, message.voice.file_id, caption=message.caption)
            elif message.content_type == 'sticker':
                await bot_tests.send_sticker(user_id, message.sticker.file_id)
            elif message.content_type == 'video_note':  # Обработка видео-сообщений
                await bot_tests.send_video_note(user_id, message.video_note.file_id)  # Отправка видео-сообщения
            elif message.content_type == 'document':  # Обработка документов
                await bot_tests.send_document(user_id, message.document.file_id, caption=message.caption) #Отправка документа
        except Exception as e:
            await message.reply(f"Не удалось отправить сообщение всем зарегистрированным пользователям {user_id}: {e}")

    await message.reply("Сообщение отправлено всем зарегистрированным пользователям.")
    await state.finish()

@dp.message_handler(lambda message: message.text == "Удалить пользователя")
async def delete_user(message: types.Message):
    await AdminStates.waiting_for_user_id_to_delete.set()
    user_list = "\n".join(
        [f"ID: {user_id}, Имя: {user['name']}" for user_id, user in registered_users.items()])
    await message.reply(f"Введите ID пользователя, которого хотите удалить:\n{user_list}")

@dp.message_handler(state=AdminStates.waiting_for_user_id_to_delete)
async def remove_user(message: types.Message, state: FSMContext):
    user_id = int(message.text)

    if user_id in registered_users:
        del registered_users[user_id]
        await message.reply(f"Пользователь с ID {user_id} был удален.")
    else:
        await message.reply("Пользователь с таким ID не найден.")

    await state.finish()

@dp.callback_query_handler(text='consultation')
async def consultation(call):
    await call.message.answer(bot_test.texsts.consultation_text, reply_markup=consultation_kb)
    await call.answer()

@dp.callback_query_handler(text='free_courses')
async def free_courses(call):
    with open('photo_4.jpg', 'rb') as img:
        await call.message.answer_photo(img, bot_test.texsts.free_courses_text, parse_mode=types.ParseMode.HTML, reply_markup=free_courses_kb)
        await call.answer()

@dp.callback_query_handler(text='about_instagram')
async def about_instagram(call):
    with open('photo_3.jpg', 'rb') as img:
        await call.message.answer_photo(img, bot_test.texsts.about_instagram_text, reply_markup=about_instagram_kb)
        await call.answer()

@dp.callback_query_handler(text='story_notebook')
async def story_notebook(call):
    with open('photo_3.jpg', 'rb') as img:
        await call.message.answer_photo(img, bot_test.texsts.story_notebook_text)
    with open('file_1.docx', 'rb') as file:
        await call.message.reply_document(file, reply_markup=story_notebook_kb)
    await call.answer()

@dp.callback_query_handler(text='inst_marathon')
async def inst_marathon(call):
    with open('photo_2.jpg', 'rb') as img:
        await call.message.answer_photo(img, bot_test.texsts.instagram_marathon_text, parse_mode=types.ParseMode.HTML, reply_markup=instagram_marathon_kb)
        await call.answer()

@dp.callback_query_handler(text='ask_question')
async def ask_question(call):
    await call.message.answer(bot_test.texsts.question_text, reply_markup=ask_question_kb)
    await call.answer()

@dp.callback_query_handler(text='back_list')
async def back_list(call):
    with open('photo_5.jpg', 'rb') as img:
        await call.message.answer_photo(img, bot_test.texsts.about_instagram_text, reply_markup=about_instagram_kb)
        await call.answer()

@dp.callback_query_handler(text='back_menu')
async def back_menu(call):
    with open('photo_6.jpg', 'rb') as img:
        await call.message.answer_photo(img, f'Добро пожаловать, {call.from_user.full_name}!👋\n' + bot_test.texsts.start_text, parse_mode=types.ParseMode.HTML, reply_markup=start_kb)
        await call.answer()

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
