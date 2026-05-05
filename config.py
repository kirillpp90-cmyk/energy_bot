import os
from dotenv import load_dotenv

# Загружаем .env файл явно
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

admin_ids_str = os.getenv("ADMIN_IDS", "")
admin_ids = [int(id) for id in admin_ids_str.split(",") if id] if admin_ids_str else []

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не найден! Установите его в .env файле")

print(f"Токен загружен: {BOT_TOKEN[:20]}...")

