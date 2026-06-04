from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from asyncio import sleep
from aiogram.filters import Command

from states import CalcState
from keyboards import cancel_kb, calculator_kb, save_after_calc_kb
from utils import calculate_energy
from database import get_user_tariff, add_device

router = Router(name="calc_router")

@router.message(Command("calc"))
@router.message(F.text == '📊 Калькулятор')
async def start_calc(message: Message, state: FSMContext):
    await message.answer(
        "⚡ Введите мощность прибора в Ваттах\n\n"
        "Например: 1500 (для чайника) или 60 (для лампы)",
        reply_markup=cancel_kb
    )
    await state.set_state(CalcState.waiting_power)

@router.message(F.text.casefold() == "отмена")
async def otmena(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("❌ Отменено", reply_markup=calculator_kb)

@router.message(CalcState.waiting_power)
async def process_power(message: Message, state: FSMContext):
    try:
        power = float(message.text.replace(',', '.'))
        if not (1 <= power <= 100_000):
            await message.answer(
                "❌ Мощность должна быть от 1 до 100 000 Ватт.\nПопробуйте ещё раз:",
                reply_markup=cancel_kb
            )
            return
        await state.update_data(power=power)
        await message.answer("⏰ Теперь введите количество часов работы в сутки (1–24):")
        await state.set_state(CalcState.waiting_hours)
    except ValueError:
        await message.answer("❌ Введите число, например: 1500", reply_markup=cancel_kb)

@router.message(CalcState.waiting_hours)
async def process_hours(message: Message, state: FSMContext):
    try:
        hours = float(message.text.replace(',', '.'))
        if not (1 <= hours <= 24):
            await message.answer(
                "❌ Часы должны быть от 1 до 24.\nПопробуйте ещё раз:",
                reply_markup=cancel_kb
            )
            return
        await state.update_data(hours=hours)
        await message.answer("📅 Теперь введите количество дней (1–365):")
        await state.set_state(CalcState.waiting_days)
    except ValueError:
        await message.answer("❌ Введите число, например: 8", reply_markup=cancel_kb)

@router.message(CalcState.waiting_days)
async def process_days(message: Message, state: FSMContext):
    try:
        days = float(message.text.replace(',', '.'))
        if not (1 <= days <= 365):
            await message.answer(
                "❌ Дни должны быть от 1 до 365.\nПопробуйте ещё раз:",
                reply_markup=cancel_kb
            )
            return
        await state.update_data(days=days)

        tariff = await get_user_tariff(message.from_user.id)

        data = await state.get_data()
        total_kwh, cost = calculate_energy(
            data['power'],
            data['hours'],
            days,
            tariff
        )

        msg = await message.answer("🔄 Начинаю расчёт...")
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
            f"📊 Результаты расчёта:\n\n"
            f"⚡ Энергопотребление: <b>{total_kwh:.2f}</b> кВт·ч\n"
            f"💰 Стоимость: <b>{cost:.2f}</b> руб (тариф {tariff} руб/кВт·ч)\n\n"
            f"🎉 Расчёт завершён успешно!",
            parse_mode="HTML"
        )

        await state.update_data(
            power=data['power'],
            hours=data['hours'],
            days=days,
            tariff=tariff,
            total_kwh=total_kwh,
            cost=cost
        )

        await message.answer('💾 Хотите сохранить этот прибор?', reply_markup=save_after_calc_kb)

    except ValueError:
        await message.answer("❌ Ошибка! Пожалуйста, введите корректное число.", reply_markup=cancel_kb)

@router.callback_query(F.data == 'save_from_calc')
async def save_from_calc(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    data = await state.get_data()
    await state.set_state(CalcState.waiting_device_name)
    await callback.message.answer(
        "✍️ Введите название для сохранения прибора:\n\n"
        f"📊 Мощность: {data['power']} Вт\n"
        f"⏰ Часов в день: {data['hours']}\n"
        f"📅 Дней: {data['days']}"
    )

@router.callback_query(F.data == 'new_calc')
async def new_calc(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.clear()
    await callback.message.answer(
        "⚡ Введите мощность прибора в Ваттах\n\n"
        "Например: 1500 (для чайника) или 60 (для лампы)",
        reply_markup=cancel_kb
    )
    await state.set_state(CalcState.waiting_power)

@router.callback_query(F.data == 'main_menu')
async def back_to_main_menu(callback: CallbackQuery, state: FSMContext):
    """Возврат в главное меню — убираем инлайн и отправляем новое с Reply-клавиатурой"""
    await callback.answer()
    await state.clear()
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer(
        "🏠 Вы в главном меню",
        reply_markup=calculator_kb
    )

@router.message(CalcState.waiting_device_name)
async def process_device_name_from_calc(message: Message, state: FSMContext):
    try:
        name = message.text.strip()
        user_id = message.from_user.id

        data = await state.get_data()
        power = data['power']
        hours = data['hours']
        days = int(data['days'])

        device_id = await add_device(user_id, name, power, hours, days)
        await state.clear()

        await message.answer(
            f'✅ Прибор "<b>{name}</b>" сохранён!\n\n'
            f'📊 Мощность: {power} Вт\n'
            f'⏰ Часов в день: {hours}\n'
            f'📅 Дней: {days}\n'
            f'🔑 ID прибора: {device_id}\n\n'
            f'Посмотреть все приборы: кнопка «📱 Приборы»',
            parse_mode="HTML",
            reply_markup=calculator_kb
        )
    except Exception as e:
        print(f"Ошибка при сохранении прибора: {e}")
        await message.answer('❌ Ошибка при сохранении. Попробуйте ещё раз.', reply_markup=calculator_kb)
        await state.clear()