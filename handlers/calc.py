from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from asyncio import sleep
from aiogram.filters import Command

from states import CalcState
from keyboards import cancel_kb, calculator_kb, save_after_calc_kb
from utils import calculate_energy
from database import init_db   # пока не используем, но оставим для будущего

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
    await message.answer("❌Отменено❌", reply_markup=calculator_kb)


@router.message(CalcState.waiting_power)
async def process_power(message: Message, state: FSMContext):
    try:
        power = float(message.text.replace(',', '.'))
        if power < 0:
            await message.answer("❌ Мощность не может быть отрицательной. Введите корректное число:", reply_markup=cancel_kb)
            return
        await state.update_data(power=power)
        await message.answer("⏰ Теперь введите количество часов работы в сутки:")
        await state.set_state(CalcState.waiting_hours)
    except ValueError:
        await message.answer("❌ Ошибка! Пожалуйста, введите корректное число.", reply_markup=cancel_kb)


@router.message(CalcState.waiting_hours)
async def process_hours(message: Message, state: FSMContext):
    try:
        hours = float(message.text.replace(',', '.'))
        if hours < 0:
            await message.answer("❌ Часы не могут быть отрицательными. Введите корректное число:", reply_markup=cancel_kb)
            return
        await state.update_data(hours=hours)
        await message.answer("📅 Теперь введите количество дней:")
        await state.set_state(CalcState.waiting_days)
    except ValueError:
        await message.answer("❌ Ошибка! Пожалуйста, введите корректное число.", reply_markup=cancel_kb)


@router.message(CalcState.waiting_days)
async def process_days(message: Message, state: FSMContext):
    try:
        days = float(message.text.replace(',', '.'))
        if days < 0:
            await message.answer("❌ Количество дней не может быть отрицательным. Введите корректное число:", reply_markup=cancel_kb)
            return
        await state.update_data(days=days)
        await message.answer("💰 Теперь введите тариф за 1 кВт·ч (в рублях):")
        await state.set_state(CalcState.waiting_tariff)
    except ValueError:
        await message.answer("❌ Ошибка! Пожалуйста, введите корректное число.", reply_markup=cancel_kb)


@router.message(CalcState.waiting_tariff)
async def process_tariff(message: Message, state: FSMContext):
    try:
        tariff = float(message.text.replace(',', '.'))
        if tariff < 0:
            await message.answer("❌ Тариф не может быть отрицательным. Введите корректное число:", reply_markup=cancel_kb)
            return
        data = await state.get_data()

        total_kwh, cost = calculate_energy(
            data['power'],
            data['hours'],
            data['days'],
            tariff
        )

        # Небольшая анимация подсчёта (как было у тебя)
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

        await msg.edit_text(f"📊 Результаты расчёта:\n\n"
                           f"⚡ Энергопотребление: <b>{total_kwh:.2f}</b> кВт·ч\n"
                           f"💰 Стоимость: <b>{cost:.2f}</b> рублей\n\n"
                           f"🎉 Расчёт завершён успешно!", parse_mode="HTML")
        
        # Сохраняем данные в состоянии для возможного сохранения прибора
        await state.update_data(
            power=data['power'],
            hours=data['hours'], 
            days=data['days'],
            tariff=tariff,
            total_kwh=total_kwh,
            cost=cost
        )
        
        await message.answer('💾 Хотите сохранить этот прибор?', reply_markup=save_after_calc_kb)

    except ValueError:
        await message.answer("❌ Ошибка! Пожалуйста, введите корректное число.", reply_markup=cancel_kb)


@router.callback_query(F.data == 'save_from_calc')
async def save_from_calc(callback: CallbackQuery, state: FSMContext):
    """Сохранение прибора из данных калькулятора"""
    await callback.answer()
    
    # Получаем данные из состояния
    data = await state.get_data()
    
    # Запрашиваем только название прибора, остальные данные уже есть
    await state.set_state(CalcState.waiting_device_name)
    await callback.message.answer(
        "✍️ Введите название для сохранения прибора:\n\n"
        f"📊 Мощность: {data['power']} Вт\n"
        f"⏰ Часов в день: {data['hours']}\n"
        f"📅 Дней: {data['days']}"
    )


@router.callback_query(F.data == 'new_calc')
async def new_calc(callback: CallbackQuery, state: FSMContext):
    """Начать новый расчет"""
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
    """Возврат в главное меню"""
    await callback.answer()
    await state.clear()
    await callback.message.answer(
        "🏠 Вы в главном меню", 
        reply_markup=calculator_kb
    )


@router.message(CalcState.waiting_device_name)
async def process_device_name_from_calc(message: Message, state: FSMContext):
    """Обработка названия прибора из калькулятора"""
    try:
        name = str(message.text.replace(',', '.'))
        user_id = int(message.from_user.id)
        
        # Получаем сохраненные данные из калькулятора
        data = await state.get_data()
        power = data['power']
        hours = data['hours']
        days = int(data['days'])  # days может быть float, преобразуем в int
        
        # Сохраняем в базу данных
        from database import add_device
        device_id = await add_device(user_id, name, power, hours, days)
        
        # Очищаем состояние
        await state.clear()
        
        # Отправляем подтверждение
        await message.answer(
            f'✅ Прибор "{name}" успешно сохранен!\n'
            f'📊 Мощность: {power} Вт\n'
            f'⏰ Часов в день: {hours}\n'
            f'📅 Дней в месяц: {days}\n\n'
            f'ID прибора: {device_id}\n\n'
            f'🔄 Хотите рассчитать что-то ещё?',
            reply_markup=calculator_kb
        )
    except Exception as e:
        # Логируем ошибку для отладки, пользователю показываем общее сообщение
        print(f"Ошибка при сохранении прибора: {e}")
        await message.answer('❌ Ошибка при сохранении. Попробуйте еще раз.', reply_markup=calculator_kb)
        await state.clear()