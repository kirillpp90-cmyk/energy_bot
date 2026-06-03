from aiogram import Router, Bot, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command

from keyboards import quick_calc_kb, calculator_kb
from database import get_user_tariff

router = Router()

Houses = {
    "quick_1room": ("1-комнатная квартира", 150),
    "quick_2room": ("2-комнатная квартира", 220),
    "quick_3room": ("3-комнатная квартира", 320),
    "quick_house": ("Частный дом", 500),
}

@router.message(Command('quick'))
@router.message(F.text == '⚡ Быстрый расчёт')
async def quick_calc_start(message: Message):
    await message.answer('⚡ Выберите тип жилья для быстрого расчёта:', reply_markup=quick_calc_kb)


@router.callback_query(F.data.startswith('quick_'))
async def quick_calc_result(callback: CallbackQuery):
    await callback.answer()
    key = callback.data
    if key not in Houses:
        await callback.message.edit_text("❌ Неизвестный тип жилья.")
        return

    name, kwh = Houses[key]

    # Берём тариф пользователя из БД
    tariff = await get_user_tariff(callback.from_user.id)

    min_cost = kwh * tariff * 0.85
    max_cost = kwh * tariff * 1.15

    await callback.message.edit_text(
        f"⚡ <b>{name}</b>\n\n"
        f"Среднее потребление: <b>{kwh}</b> кВт·ч/мес\n"
        f"Тариф: <b>{tariff}</b> руб/кВт·ч\n"
        f"Стоимость (±15%): <b>{min_cost:.0f} — {max_cost:.0f} руб</b>\n\n"
        f"<i>Чтобы изменить тариф — нажмите «💰 Тариф» в меню</i>"
    )


@router.callback_query(F.data == 'otmena')
async def otmena_quick(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_text("❌ Отменено")
