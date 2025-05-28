from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.dispatcher import filters
from mainbot import dp, bot_tests

# ID администратора (ваш Telegram ID)
ADMIN_ID = 1060502535  # Замените на ваш ID

# Список зарегистрированных пользователей (пример)
registered_users = {}

class AdminStates(StatesGroup):
    waiting_for_users_selection = State()
    waiting_for_message = State()
    waiting_for_user_ids_to_send_message = State()
    waiting_for_user_id_to_delete = State()
    waiting_for_new_name = State()

# Команда /admin
@dp.message_handler(commands=['admin'])
async def cmd_admin(message: types.Message):
    if message.from_user.id == ADMIN_ID:
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add("Список пользователей", "Отправить всем сообщение", "Отправить сообщение выбранным пользователям",
                 "Удалить пользователя")
        await message.answer("Панель администратора", reply_markup=keyboard)
    else:
        await message.answer("У вас нет доступа к админ-панели.")


# Обработка кнопок админ-панели
@dp.message_handler(lambda message: message.text == "Список пользователей")
async def list_users(message: types.Message):
    if not registered_users:
        await message.reply("Нет зарегистрированных пользователей.")
        return

    user_list = "\n".join(
        [f"ID: {user_id}, Имя: {user['name']}" for user_id, user in registered_users.items()])
    await message.reply(f"Список зарегистрированных пользователей:\n{user_list}")

@dp.message_handler(lambda message: message.text == "Отправить сообщение выбранным пользователям")
async def select_users_to_send_message(message: types.Message, state: FSMContext):
    await AdminStates.waiting_for_users_selection.set()

    if not registered_users:
        await message.reply("Нет зарегистрированных пользователей.")
        await state.finish()
        return

    user_list = "\n".join([f"ID: {user_id}, Имя: {user['name']}" for user_id, user in registered_users.items()])
    await message.reply(f"Выберите пользователей по ID (через запятую):\n{user_list}")


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
        await AdminStates.waiting_for_message.set()
        await message.reply("Введите сообщение для выбранных пользователей:")
    else:
        await message.reply("Нет валидных ID пользователей. Попробуйте снова.")
        await state.finish()


@dp.message_handler(state=AdminStates.waiting_for_message)
async def process_message_to_selected(message: types.Message, state: FSMContext):
    data = await state.get_data()
    valid_user_ids = data.get('valid_user_ids', [])

    if valid_user_ids:
        for user_id in valid_user_ids:
            try:
                await bot_tests.send_message(user_id, message.text)
            except Exception as e:
                await message.reply(f"Не удалось отправить сообщение пользователю {user_id}: {e}")

        await message.reply("Сообщение отправлено выбранным пользователям.")
    else:
        await message.reply("Не было выбрано ни одного пользователя для отправки сообщения.")
    await state.finish()

@dp.message_handler(lambda message: message.text == "Отправить всем сообщение")
async def send_message_to_all(message: types.Message):
    await AdminStates.waiting_for_message.set()
    await message.reply("Введите сообщение для всех зарегистрированных пользователей:")


@dp.message_handler(state=AdminStates.waiting_for_message)
async def process_message_to_all(message: types.Message, state: FSMContext):
    for user_id in registered_users.keys():
        await bot_tests.send_message(user_id, message.text)

    await message.reply("Сообщение отправлено всем зарегистрированным пользователям.")
    await state.finish()

@dp.message_handler(lambda message: message.text == "Удалить пользователя")
async def delete_user(message: types.Message):
    await AdminStates.waiting_for_user_id_to_delete.set()
    await message.reply("Введите ID пользователя, которого хотите удалить:")


@dp.message_handler(state=AdminStates.waiting_for_user_id_to_delete)
async def remove_user(message: types.Message, state: FSMContext):
    user_id = int(message.text)

    if user_id in registered_users:
        del registered_users[user_id]
        await message.reply(f"Пользователь с ID {user_id} был удален.")
    else:
        await message.reply("Пользователь с таким ID не найден.")

    await state.finish()

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)