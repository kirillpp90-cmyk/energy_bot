from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

from keyboards import calculator_kb
from database import get_or_create_user

router = Router()

@router.message(Command("start"))
async def cmd_start(message: Message):
    await get_or_create_user(
        message.from_user.id,
        message.from_user.first_name,
        message.from_user.last_name,
        message.from_user.username
    )
    await message.answer(
        f"👋 Привет, {message.from_user.full_name}!\n\n"
        "⚡ <b>Добро пожаловать в бот-калькулятор энергопотребления!</b>\n\n"
        "🎯 Здесь вы можете:\n"
        "• Рассчитать энергопотребление приборов\n"
        "• Узнать стоимость электроэнергии\n"
        "• Получить помощь по использованию\n\n"
        "ℹ️ Используйте команду /about чтобы узнать подробнее", reply_markup=calculator_kb
    )