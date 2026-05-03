import aiosqlite
import asyncio

# Глобальная блокировка для записи в БД (чтобы не было конфликтов)
_db_lock = asyncio.Lock()


async def get_user_count():
    """Возвращает количество пользователей в базе"""
    connect = await aiosqlite.connect('db.db')
    cursor = await connect.cursor()
    await cursor.execute('SELECT COUNT(*) FROM users')
    user_count = await cursor.fetchone()
    await cursor.close()
    await connect.close()
    return user_count[0]


async def get_all_users_id():
    """Возвращает список всех user_id"""
    connect = await aiosqlite.connect('db.db')
    cursor = await connect.cursor()
    await cursor.execute('SELECT user_id FROM users')
    users = await cursor.fetchall()
    await cursor.close()
    await connect.close()
    return [user[0] for user in users]


async def init_db():
    """Создаёт таблицы users и devices, если их нет"""
    connect = await aiosqlite.connect('db.db')
    cursor = await connect.cursor()

    # Таблица users
    await cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY
        )
    ''')

    # Таблица devices
    await cursor.execute('''
        CREATE TABLE IF NOT EXISTS devices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            name TEXT,
            power_watt REAL,
            hours_per_day REAL,
            days INTEGER
        )
    ''')

    await connect.commit()
    await cursor.close()
    await connect.close()
    print("✅ База данных инициализирована (db.db) с таблицами users и devices")


async def get_or_create_user(user_id: int):
    """Проверяет, есть ли пользователь в БД, если нет — создаёт с защитой от гонок"""
    async with _db_lock:  # Блокируем запись для всех, кто вызывает эту функцию одновременно
        connect = await aiosqlite.connect('db.db')
        cursor = await connect.cursor()
        try:
            await cursor.execute('SELECT user_id FROM users WHERE user_id = ?', (user_id,))
            exists = await cursor.fetchone()
            if not exists:
                await cursor.execute('INSERT INTO users (user_id) VALUES (?)', (user_id,))
                await connect.commit()
        finally:
            await cursor.close()
            await connect.close()


async def add_device(user_id: int, name: str, power_watt: float, hours_per_day: float, days: int):
    """Добавляет прибор в таблицу devices с защитой от одновременной записи"""
    async with _db_lock:
        connect = await aiosqlite.connect('db.db')
        cursor = await connect.cursor()
        try:
            await cursor.execute('''
                INSERT INTO devices (user_id, name, power_watt, hours_per_day, days)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, name, power_watt, hours_per_day, days))
            await connect.commit()
            last_id = cursor.lastrowid
        finally:
            await cursor.close()
            await connect.close()
        return last_id


async def get_user_devices(user_id: int):
    """Возвращает список приборов пользователя в виде словарей (через row_factory)"""
    connect = await aiosqlite.connect('db.db')
    connect.row_factory = aiosqlite.Row  # Включаем доступ по имени колонки
    cursor = await connect.cursor()
    await cursor.execute('SELECT * FROM devices WHERE user_id = ?', (user_id,))
    rows = await cursor.fetchall()
    # Превращаем Row в обычный dict для удобства (можно и так оставить, но dict привычнее)
    devices = [dict(row) for row in rows]
    await cursor.close()
    await connect.close()
    return devices


async def delete_device(device_id: int, user_id: int) -> bool:
    """Удаляет прибор, если он принадлежит пользователю. Возвращает True, если удалён"""
    async with _db_lock:
        connect = await aiosqlite.connect('db.db')
        cursor = await connect.cursor()
        try:
            await cursor.execute('DELETE FROM devices WHERE id = ? AND user_id = ?', (device_id, user_id))
            await connect.commit()
            deleted = cursor.rowcount > 0
        finally:
            await cursor.close()
            await connect.close()
        return deleted


async def clear_user_devices(user_id: int):
    """Удаляет все приборы пользователя (опционально)"""
    async with _db_lock:
        connect = await aiosqlite.connect('db.db')
        cursor = await connect.cursor()
        try:
            await cursor.execute('DELETE FROM devices WHERE user_id = ?', (user_id,))
            await connect.commit()
        finally:
            await cursor.close()
            await connect.close()