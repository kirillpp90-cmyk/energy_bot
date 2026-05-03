# main.py
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config import BOT_TOKEN
from database import init_db

# Импорт роутеров
from handlers.start import router as start_router
from handlers.calc import router as calc_router
from handlers.about import router as about_router
from handlers.menu import router as menu_router
from handlers.help import router as help_router
from handlers.admin import router as admin_router

async def main():
    # Инициализация базы данных
    await init_db()

    # Новый способ задания parse_mode в aiogram 3.7+
    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )

    dp = Dispatcher()

    # Подключаем роутеры
    dp.include_router(start_router)
    dp.include_router(calc_router)
    dp.include_router(about_router)
    dp.include_router(menu_router)
    dp.include_router(help_router)
    dp.include_router(admin_router)

    print("🚀 Бот успешно запущен и готов к работе!")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())