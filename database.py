import aiosqlite
import asyncio

_db_lock = asyncio.Lock()


async def get_user_count():
    connect = await aiosqlite.connect('db.db')
    cursor = await connect.cursor()
    await cursor.execute('SELECT COUNT(*) FROM users')
    user_count = await cursor.fetchone()
    await cursor.close()
    await connect.close()
    return user_count[0]


async def get_all_users_id():
    connect = await aiosqlite.connect('db.db')
    cursor = await connect.cursor()
    await cursor.execute('SELECT user_id FROM users')
    users = await cursor.fetchall()
    await cursor.close()
    await connect.close()
    return [user[0] for user in users]


async def get_all_users_info():
    connect = await aiosqlite.connect('db.db')
    cursor = await connect.cursor()
    await cursor.execute('SELECT user_id, username, first_name, last_name FROM users')
    users = await cursor.fetchall()
    await cursor.close()
    await connect.close()
    return users


async def init_db():
    connect = await aiosqlite.connect('db.db')
    cursor = await connect.cursor()

    await cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            last_name TEXT,
            tariff REAL DEFAULT 5.5
        )
    ''')

    await cursor.execute("PRAGMA table_info(users)")
    columns = [col[1] for col in await cursor.fetchall()]
    for col, coltype in [
        ('tariff', 'REAL DEFAULT 5.5'),
        ('username', 'TEXT'),
        ('first_name', 'TEXT'),
        ('last_name', 'TEXT'),
    ]:
        if col not in columns:
            await cursor.execute(f"ALTER TABLE users ADD COLUMN {col} {coltype}")

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
    print("База данных инициализирована (db.db) с таблицами users и devices")


async def get_user_tariff(user_id: int) -> float:
    connect = await aiosqlite.connect('db.db')
    cursor = await connect.cursor()
    await cursor.execute('SELECT tariff FROM users WHERE user_id = ?', (user_id,))
    row = await cursor.fetchone()
    await cursor.close()
    await connect.close()
    if row:
        return row[0]
    return 5.5


async def update_user_tariff(user_id: int, tariff: float):
    async with _db_lock:
        connect = await aiosqlite.connect('db.db')
        cursor = await connect.cursor()
        try:
            await cursor.execute('UPDATE users SET tariff = ? WHERE user_id = ?', (tariff, user_id))
            await connect.commit()
        finally:
            await cursor.close()
            await connect.close()


async def get_or_create_user(user_id: int, first_name: str = None, last_name: str = None, username: str = None):
    async with _db_lock:
        connect = await aiosqlite.connect('db.db')
        cursor = await connect.cursor()
        try:
            await cursor.execute('SELECT user_id FROM users WHERE user_id = ?', (user_id,))
            exists = await cursor.fetchone()
            if not exists:
                await cursor.execute(
                    'INSERT INTO users (user_id, first_name, last_name, username, tariff) VALUES (?, ?, ?, ?, ?)',
                    (user_id, first_name, last_name, username, 5.5)
                )
                await connect.commit()
        finally:
            await cursor.close()
            await connect.close()


async def add_device(user_id: int, name: str, power_watt: float, hours_per_day: float, days: int):
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
    connect = await aiosqlite.connect('db.db')
    connect.row_factory = aiosqlite.Row
    cursor = await connect.cursor()
    await cursor.execute('SELECT * FROM devices WHERE user_id = ?', (user_id,))
    rows = await cursor.fetchall()
    devices = [dict(row) for row in rows]
    await cursor.close()
    await connect.close()
    return devices


async def delete_device(device_id: int, user_id: int) -> bool:
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
    async with _db_lock:
        connect = await aiosqlite.connect('db.db')
        cursor = await connect.cursor()
        try:
            await cursor.execute('DELETE FROM devices WHERE user_id = ?', (user_id,))
            await connect.commit()
        finally:
            await cursor.close()
            await connect.close()
