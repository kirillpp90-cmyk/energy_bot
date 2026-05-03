from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

from keyboards import calculator_kb

router = Router()

@router.message(Command('menu'))
async def menu(message: Message):
    await message.answer('Вот меню!', reply_markup=calculator_kb)
