from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

from keyboards import calculator_kb

router = Router()

@router.message(Command('menu'))
async def menu(message: Message):
    await message.answer(
        '📋 <b>Главное меню</b>\n\n'
        'Доступные функции:\n\n'
        '📊 <b>Калькулятор</b> — точный расчёт: введите мощность, часы и дни вручную\n\n'
        '⚡ <b>Быстрый расчёт</b> — выберите тип жилья, получите оценку за секунду\n\n'
        '📱 <b>Приборы</b> — список сохранённых приборов и общий расчёт по ним\n\n'
        '💰 <b>Тариф</b> — посмотреть и изменить ваш тариф (руб/кВт·ч)\n\n'
        '❓ <b>Помощь</b> — написать в поддержку (текст, фото, документы)\n\n'
        'ℹ️ <b>О боте</b> — информация о боте и список команд',
        parse_mode='HTML',
        reply_markup=calculator_kb
    )