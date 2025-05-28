import sqlite3
from distutils.command.check import check

connection = sqlite3.connect('not_telegram.db')
cursor = connection.cursor()

#создаем таблицу
cursor.execute('''
    CREATE TABLE IF NOT EXISTS Users(
    id INTEGER,
    username TEXT,
    first_name TEXT,
    block INTEGER
    );
''')

#Проверяется пользователь на наличие в бд, вернётся либо 'None', если пользователя нет в базе, либо информация о пользователе.
#Если пользователь не найден, его необходимо добавить (0 - означает, что пользователь не заблокирован).
def add_user(user_id, username, first_name):
    check_user = cursor.execute('SELECT * FROM Users WHERE id = ?', (user_id,))
    if check_user.fetchone() is None:
        cursor.execute(f'''INSERT INTO Users VALUES('{user_id}', '{username}', '{first_name}', 0)''')
    connection.commit() #сохраняем состояние базы данных

#функция для вывода списка всех пользователей
def show_users():
    users_list = cursor.execute('SELECT * FROM USERS') #получение списка пользователей из бд
    message = '' #создаётся сообщение, которое будет постепенно наполняться данными. Изначально сообщение остаётся пустым
    for user in users_list: #цикл по дополнению сообщения
        message += f'{user[0]} @{user[1]} {user[2]} \n' #где user[0] — это id, user[1] — username, user[2] — first_name,
        # \n — это перенос строки
    connection.commit() #сохраняем изменения в сообщении
    return message #возвращаем готовое сообщение

#функция по подсчету общего числа пользователей
def show_stat():
    count_users = cursor.execute('SELECT COUNT(*) FROM Users').fetchone()
    connection.commit()
    return count_users[0]

#функция по добавлению пользователя в блокировку
def add_to_block(input_id):
    cursor.execute(f'UPDATE Users SET block = ? WHERE id = ?', (1, input_id))
    connection.commit()

#функция по убиранию пользователя из блокировки
def remove_block(input_id):
    cursor.execute(f'UPDATE Users SET block = ? WHERE id = ?', (0, input_id))
    connection.commit()

#функция по проверке пользователя находится ли он в блокировке
def check_block(user_id):
    users = cursor.execute(f'SELECT block FROM Users WHERE id = {user_id}').fetchone()
    connection.commit()
    return users[0]


connection.commit()
connection.close()