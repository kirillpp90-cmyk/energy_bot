from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from database import get_user_tariff, update_user_tariff
from keyboards import calculator_kb, cancel_kb
from states import TariffState

router = Router()

@router.message(Command("tariff"))
@router.message(F.text == "💰 Тариф")
async def show_tariff(message: Message):
    tariff = await get_user_tariff(message.from_user.id)
    await message.answer(
        f"💰 <b>Ваш текущий тариф</b>: {tariff} руб/кВт·ч\n\n"
        "Изменить тариф можно командой /set_tariff",
        parse_mode="HTML"
    )

@router.message(Command("set_tariff"))
async def set_tariff_start(message: Message, state: FSMContext):
    await message.answer(
        "✏️ Введите новый тариф в рублях за 1 кВт·ч.\n\n"
        "Например: 5.6 или 4.2",
        reply_markup=cancel_kb
    )
    await state.set_state(TariffState.waiting_tariff_value)

@router.message(TariffState.waiting_tariff_value)
async def set_tariff_value(message: Message, state: FSMContext):
    try:
        tariff = float(message.text.replace(',', '.'))
        if tariff <= 0:
            await message.answer("❌ Тариф должен быть положительным числом. Попробуйте ещё раз.")
            return
        await update_user_tariff(message.from_user.id, tariff)
        await message.answer(
            f"✅ Тариф успешно установлен: {tariff} руб/кВт·ч",
            reply_markup=calculator_kb
        )
        await state.clear()
    except ValueError:
        await message.answer("❌ Ошибка! Введите корректное число (например, 5.6).", reply_markup=cancel_kb)

@router.message(F.text == "Отмена", TariffState.waiting_tariff_value)
async def cancel_tariff(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("❌ Установка тарифа отменена.", reply_markup=calculator_kb)