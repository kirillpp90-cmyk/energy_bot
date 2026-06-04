from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from database import get_user_tariff, update_user_tariff
from keyboards import calculator_kb, cancel_kb
from states import TariffState

router = Router()

def tariff_info_kb():
    """Клавиатура под сообщением с тарифом"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✏️ Изменить тариф", callback_data="change_tariff")]
    ])

@router.message(Command("tariff"))
@router.message(F.text == "💰 Тариф")
async def show_tariff(message: Message):
    tariff = await get_user_tariff(message.from_user.id)
    await message.answer(
        f"💰 <b>Ваш текущий тариф</b>: {tariff} руб/кВт·ч\n\n"
        f"Этот тариф используется во всех расчётах.\n"
        f"Нажмите кнопку ниже чтобы изменить.",
        parse_mode="HTML",
        reply_markup=tariff_info_kb()
    )

@router.callback_query(F.data == "change_tariff")
async def change_tariff_callback(callback: CallbackQuery, state: FSMContext):
    """Кнопка «Изменить тариф» из инлайн-клавиатуры"""
    await callback.answer()
    await callback.message.answer(
        "✏️ Введите новый тариф в рублях за 1 кВт·ч.\n\n"
        "Например: <b>5.6</b> или <b>4.2</b>\n\n"
        "Средние тарифы по РФ:\n"
        "• Москва — 6.99\n"
        "• МО — 6.17\n"
        "• СПб — 6.19\n"
        "• ЦФО — 5.81\n"
        "• ПФО — 4.93\n"
        "• СФО — 4.12\n"
        "• ЮФО — 5.28\n"
        "• УФО — 3.96",
        parse_mode="HTML",
        reply_markup=cancel_kb
    )
    await state.set_state(TariffState.waiting_tariff_value)

@router.message(Command("set_tariff"))
async def set_tariff_start(message: Message, state: FSMContext):
    """Команда /set_tariff — тоже запускает изменение тарифа"""
    await message.answer(
        "✏️ Введите новый тариф в рублях за 1 кВт·ч.\n\n"
        "Например: <b>5.6</b> или <b>4.2</b>",
        parse_mode="HTML",
        reply_markup=cancel_kb
    )
    await state.set_state(TariffState.waiting_tariff_value)

@router.message(TariffState.waiting_tariff_value)
async def set_tariff_value(message: Message, state: FSMContext):
    try:
        tariff = float(message.text.replace(',', '.'))
        if tariff <= 0:
            await message.answer(
                "❌ Тариф должен быть положительным числом. Попробуйте ещё раз.",
                reply_markup=cancel_kb
            )
            return
        if tariff > 50:
            await message.answer(
                "❌ Слишком большое значение. Тариф обычно от 1 до 20 руб/кВт·ч.",
                reply_markup=cancel_kb
            )
            return

        await update_user_tariff(message.from_user.id, tariff)
        await state.clear()
        await message.answer(
            f"✅ Тариф успешно установлен: <b>{tariff} руб/кВт·ч</b>\n\n"
            f"Теперь все расчёты будут использовать этот тариф.",
            parse_mode="HTML",
            reply_markup=calculator_kb
        )
    except ValueError:
        await message.answer(
            "❌ Ошибка! Введите корректное число (например, 5.6).",
            reply_markup=cancel_kb
        )

@router.message(F.text == "Отмена", TariffState.waiting_tariff_value)
async def cancel_tariff(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("❌ Установка тарифа отменена.", reply_markup=calculator_kb)