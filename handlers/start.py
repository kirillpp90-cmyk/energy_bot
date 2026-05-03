from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

from keyboards import calculator_kb

router = Router()

@router.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(
        f"👋 Привет, {message.from_user.full_name}!\n\n"
        "⚡ <b>Добро пожаловать в бот-калькулятор энергопотребления!</b>\n\n"
        "🎯 Здесь вы можете:\n"
        "• Рассчитать энергопотребление приборов\n"
        "• Узнать стоимость электроэнергии\n"
        "• Получить помощь по использованию\n\n"
        "ℹ️ Используйте команду /about чтобы узнать подробнее", reply_markup=calculator_kb
    )
