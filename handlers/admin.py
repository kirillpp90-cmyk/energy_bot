from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from config import admin_ids
from database import get_user_count, get_all_users_id
import asyncio

from keyboards import cancel_kb
from states import AdminStates

router = Router()

def is_admin(user_id: int) -> bool:
    return user_id in admin_ids

@router.message(Command("admin"))
async def admin_panel(message: Message):
    if not is_admin(message.from_user.id):
        await message.answer("⛔ У вас нет доступа к админ-панели.")
        return
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 Статистика", callback_data="admin_stats")],
        [InlineKeyboardButton(text="📢 Рассылка", callback_data="admin_mailing")],
        [InlineKeyboardButton(text="👥 Список пользователей", callback_data="admin_users")]
    ])
    await message.answer("🔐 Админ-панель", reply_markup=kb)

@router.callback_query(F.data == "admin_stats")
async def admin_stats(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("Доступ запрещён", show_alert=True)
        return
    await callback.answer()
    total_users = await get_user_count()
    text = f"📊 Статистика:\n\n👥 Всего пользователей: {total_users}"
    await callback.message.edit_text(text)

@router.callback_query(F.data == "admin_mailing")
async def admin_mailing_start(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        await callback.answer("Доступ запрещён", show_alert=True)
        return
    await callback.answer()
    await callback.message.edit_text("📝 Введи текст рассылки. Он будет отправлен ВСЕМ пользователям.\n\nДля отмены - /cancel", reply_markup=cancel_kb)
    await state.set_state(AdminStates.waiting_mailing_text)

@router.message(AdminStates.waiting_mailing_text)
async def send_mailing(message: Message, state: FSMContext, bot: Bot):
    if not is_admin(message.from_user.id):
        await message.answer("⛔ Доступ запрещён")
        await state.clear()
        return
    text = message.text
    users = await get_all_users_id()
    success = 0
    fail = 0
    await message.answer(f"🚀 Начинаю рассылку {len(users)} пользователям...")
    for uid in users:
        try:
            await bot.send_message(uid, text)
            success += 1
            await asyncio.sleep(0.05)
        except Exception:
            fail += 1
    await message.answer(f"✅ Рассылка завершена.\n✅ Успешно: {success}\n❌ Провалено (бот заблокирован или ошибка): {fail}")
    await state.clear()

@router.callback_query(F.data == "admin_users")
async def admin_users(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("Доступ запрещён", show_alert=True)
        return
    await callback.answer()
    users = await get_all_users_id()
    if not users:
        await callback.message.edit_text("Нет пользователей в базе.")
        return
    text = "👥 Список пользователей (первые 10):\n"
    for uid in users[:10]:
        text += f"• <code>{uid}</code>\n"
    if len(users) > 10:
        text += f"\n... и ещё {len(users)-10} пользователей."
    await callback.message.edit_text(text, parse_mode="HTML")
    await callback.message.answer('Успешно', reply_markup=cancel_kb)

@router.message(F.text == "Отмена", AdminStates.waiting_mailing_text)
@router.message(Command("cancel"), AdminStates.waiting_mailing_text)
async def cancel_mailing(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        await message.answer("⛔ Доступ запрещён")
        await state.clear()
        return
    await state.clear()
    await message.answer("❌ Рассылка отменена", reply_markup=cancel_kb)
