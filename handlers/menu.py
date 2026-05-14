from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

from keyboards import calculator_kb

router = Router()

@router.message(Command('menu'))
async def menu(message: Message):
    await message.answer('📋 <b>Главное меню</b>\n\n'
                         'Выберите действие ниже:\n'
                         '📊 Калькулятор - расчёт энергопотребления\n'
                         '❓ Помощь - поддержка\n'
                         'ℹ️ О боте - информация\n\n'
                         '📱 Приборы - сохранённые приборы\n\n'
                         '🎯 Начните с калькулятора для расчётов!', reply_markup=calculator_kb)
