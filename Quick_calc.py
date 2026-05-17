from aiogram import Router, Bot, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command

from keyboards import quick_calc_kb

router = Router()

@router.message(Command('quick'))
@router.message(F.text == '⚡ Быстрый расчёт')
async def quick_calc(message: Message):
    await message.answer('Выберет нужный вариант:', reply_markup=quick_calc_kb)

Houses = {
    "quick_1room": ("1-комнатная квартира", 150),
    "quick_2room": ("2-комнатная квартира", 220),
    "quick_3room": ("3-комнатная квартира", 320),
    "quick_house": ("Частный дом", 500),
}

@router.callback_query(F.data.startswith('quick_'))
async def quick_calc(callback: CallbackQuery, bot: Bot):
    await callback.answer()
    housing_type = callback.data.split("_")[1]
    key = callback.data
    name, kwh = Houses[key]
    tariff = 5.5
    min_cost = kwh * tariff * 0.85
    max_cost = kwh * tariff * 1.15
    await callback.message.edit_text(
        f"⚡ <b>{name}</b>\n\n"
        f"Среднее потребление: <b>{kwh}</b> кВт·ч/мес\n"
        f"Стоимость (±15%): <b>{min_cost:.0f} — {max_cost:.0f} руб</b>")



