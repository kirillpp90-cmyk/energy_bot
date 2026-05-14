from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command

from database import get_user_devices, delete_device
from keyboards import calculator_kb

router = Router()


@router.message(F.text == "📱 Приборы")
@router.message(Command("mydevices"))
async def my_devices(message: Message):
    devices = await get_user_devices(message.from_user.id)

    if not devices:
        await message.answer("У вас пока нет сохранённых приборов.")
        return

    text = "📋 Ваши приборы:\n\n"
    for device in devices:
        text += f"• {device['name']} ({device['id']}) — {device['power_watt']} Вт\n"

    inline_keyboard = []
    for device in devices:
        inline_keyboard.append([
            InlineKeyboardButton(
                text=f"🗑 {device['name']}",
                callback_data=f"delete_{device['id']}"
            )
        ])

    kb = InlineKeyboardMarkup(inline_keyboard=inline_keyboard)

    await message.answer(text, reply_markup=kb)


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