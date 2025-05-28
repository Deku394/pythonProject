import sqlite3

def initiate_db():
    connection = sqlite3.connect('crud_functions.db')
    cursor = connection.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Products(
        id INTEGER PRIMARY KEY,
        title TEXT NOT NULL,
        description TEXT,
        price INTEGER NOT NULL
        )
    ''')
    connection.commit()
    connection.close()

def insert_db():
    connection = sqlite3.connect('crud_functions.db')
    cursor = connection.cursor()
    for i in range(1, 5):
        cursor.execute('INSERT INTO Products (id, title, description, price) VALUES (?, ?, ?, ?)',
                       (f'id{i}', f'Продукт {i}', f'Описание {i}', i * 100))
    connection.commit()
    connection.close()

def get_all_products():
    connection = sqlite3.connect('crud_functions.db')
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM Products')
    connection.close()
    return cursor.fetchall()


if __name__ == '__main__':
    initiate_db()