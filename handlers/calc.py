from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from asyncio import sleep
from aiogram.filters import Command

from states import CalcState
from keyboards import cancel_kb
from utils import calculate_energy
from database import init_db   # пока не используем, но оставим для будущего

router = Router(name="calc_router")


@router.message(Command("calc"))
async def start_calc(message: Message, state: FSMContext):
    await message.answer(
        "Введите мощность прибора в Ваттах (например: 1500):",
        reply_markup=cancel_kb
    )
    await state.set_state(CalcState.waiting_power)


@router.message(F.text.casefold() == "отмена")
async def otmena(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Расчёт отменён.", reply_markup=None)


@router.message(CalcState.waiting_power)
async def process_power(message: Message, state: FSMContext):
    try:
        power = float(message.text.replace(',', '.'))
        await state.update_data(power=power)
        await message.answer("Теперь введите количество часов работы в сутки:")
        await state.set_state(CalcState.waiting_hours)
    except ValueError:
        await message.answer("❌ Ошибка! Введите пожалуйста число.", reply_markup=cancel_kb)


@router.message(CalcState.waiting_hours)
async def process_hours(message: Message, state: FSMContext):
    try:
        hours = float(message.text.replace(',', '.'))
        await state.update_data(hours=hours)
        await message.answer("Теперь введите количество дней:")
        await state.set_state(CalcState.waiting_days)
    except ValueError:
        await message.answer("❌ Ошибка! Введите пожалуйста число.", reply_markup=cancel_kb)


@router.message(CalcState.waiting_days)
async def process_days(message: Message, state: FSMContext):
    try:
        days = float(message.text.replace(',', '.'))
        await state.update_data(days=days)
        await message.answer("Теперь введите тариф за 1 кВт·ч (в рублях):")
        await state.set_state(CalcState.waiting_tariff)
    except ValueError:
        await message.answer("❌ Ошибка! Введите пожалуйста число.", reply_markup=cancel_kb)


@router.message(CalcState.waiting_tariff)
async def process_tariff(message: Message, state: FSMContext):
    try:
        tariff = float(message.text.replace(',', '.'))
        data = await state.get_data()

        total_kwh, cost = calculate_energy(
            data['power'],
            data['hours'],
            data['days'],
            tariff
        )

        # Небольшая анимация подсчёта (как было у тебя)
        msg = await message.answer("Начинается подсчёт...")
        await sleep(0.6)
        await msg.edit_text("33%...")
        await sleep(0.4)
        await msg.edit_text("66%...")
        await sleep(0.4)
        await msg.edit_text("99%...")
        await sleep(0.4)
        await msg.edit_text("100%...")
        await sleep(0.3)

        await msg.edit_text(
            f"✅ Готово!\n\n"
            f"Энергопотребление: <b>{total_kwh:.2f}</b> кВт·ч\n"
            f"Стоимость: <b>{cost:.2f}</b> рублей",
            parse_mode="HTML"
        )

        await state.clear()

    except ValueError:
        await message.answer("❌ Ошибка! Введите пожалуйста число.", reply_markup=cancel_kb)