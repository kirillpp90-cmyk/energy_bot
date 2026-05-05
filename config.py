import os
from dotenv import load_dotenv

# Загружаем .env файл явно
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

admin_ids = [5548414556, 1347913056]

# Проверка наличия токена
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не найден! Установите его в .env файле")

print(f"Токен загружен: {BOT_TOKEN[:20]}...")
