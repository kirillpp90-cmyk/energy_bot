import aiosqlite


async def get_user_count():
    """Возвращает количество пользователей в базе"""
    connect = await aiosqlite.connect('db.db')
    cursor = await connect.cursor()
    result = await cursor.execute('SELECT COUNT(*) FROM users')
    user_count = await result.fetchone()
    await cursor.close()
    await connect.close()
    return user_count[0]


async def get_all_users_id():
    """Возвращает список всех user_id"""
    connect = await aiosqlite.connect('db.db')
    cursor = await connect.cursor()
    result = await cursor.execute('SELECT user_id FROM users')
    users = await result.fetchall()
    await cursor.close()
    await connect.close()
    users = [user[0] for user in users]
    return users


async def init_db():
    """Создаёт таблицу users, если её ещё нет"""
    connect = await aiosqlite.connect('db.db')
    cursor = await connect.cursor()

    await cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY
        )
    ''')

    await connect.commit()
    await cursor.close()
    await connect.close()
    print("✅ База данных инициализирована (db.db)")