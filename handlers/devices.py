from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command

from database import get_user_devices, delete_device, get_user_tariff
from keyboards import get_devices_kb, calculator_kb

router = Router()


@router.message(F.text == "📱 Приборы")
@router.message(Command("mydevices"))
async def my_devices(message: Message):
    devices = await get_user_devices(message.from_user.id)

    if not devices:
        await message.answer("📭 У вас пока нет сохранённых приборов.\n\nПосле расчёта нажмите «Сохранить прибор».")
        return

    text = "📋 <b>Ваши приборы</b>\n\n"
    for device in devices:
        text += f"🔹 <b>{device['name']}</b> (ID: {device['id']})\n"
        text += f"   Мощность: {device['power_watt']} Вт\n"
        text += f"   Часов/день: {device['hours_per_day']}\n"
        text += f"   Дней: {device['days']}\n\n"

    kb = get_devices_kb(devices)
    await message.answer(text, parse_mode="HTML", reply_markup=kb)

@router.callback_query(F.data.startswith("delete_"))
async def delete_device_handler(callback: CallbackQuery):
    device_id = int(callback.data.split("_")[1])
    user_id = callback.from_user.id

    deleted = await delete_device(device_id, user_id)

    if deleted:
        await callback.answer("✅ Прибор удалён")
        await callback.message.answer("✅ Прибор успешно удалён!", reply_markup=calculator_kb)
    else:
        await callback.answer("❌ Не удалось удалить прибор")

@router.callback_query(F.data == "calculate_all")
async def calculate_all_devices(callback: CallbackQuery):
    await callback.answer()
    user_id = callback.from_user.id
    devices = await get_user_devices(user_id)

    if not devices:
        await callback.message.answer("📭 Нет приборов для расчёта.")
        return

    tariff = await get_user_tariff(user_id)
    total_kwh = 0.0
    for device in devices:
        power_kw = device['power_watt'] / 1000.0
        kwh = power_kw * device['hours_per_day'] * device['days']
        total_kwh += kwh

    total_cost = total_kwh * tariff

    text = (f"📊 <b>Общий расчёт всех приборов</b>\n\n"
            f"⚡ Суммарное потребление: <b>{total_kwh:.2f}</b> кВт·ч\n"
            f"💰 Стоимость (при тарифе {tariff} руб/кВт·ч): <b>{total_cost:.2f}</b> руб.")
    await callback.message.answer(text, parse_mode="HTML", reply_markup=calculator_kb)