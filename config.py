import os
from dotenv import load_dotenv

# Загружаем .env файл явно
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

# Если токен всё равно не загрузился — используем прямую запись (временное решение)
if not BOT_TOKEN:
    BOT_TOKEN = "8603742193:AAH0pKqQ9-bTJvG7iBPAeDyrw_hfJ8Xiyxc"   # ← твой токен

print(f"Токен загружен: {BOT_TOKEN[:20]}...")   # Для проверки