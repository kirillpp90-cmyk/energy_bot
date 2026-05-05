from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, TelegramObject
from aiogram.filters import Command, BaseFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from config import admin_ids
from database import get_user_count, get_all_users_id, get_all_users_info
import asyncio

from keyboards import cancel_kb, admin_back_kb, admin_cancel_kb
from states import AdminStates

class IsAdmin(BaseFilter):
    async def __call__(self, obj: TelegramObject):
        return obj.from_user.id in admin_ids

router = Router()

@router.message(Command("admin"), IsAdmin())
async def admin_panel(message: Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 Статистика", callback_data="admin_stats")],
        [InlineKeyboardButton(text="📢 Рассылка", callback_data="admin_mailing")],
        [InlineKeyboardButton(text="👥 Список пользователей", callback_data="admin_users")]
    ])
    await message.answer("🔐 Админ-панель", reply_markup=kb)

@router.callback_query(F.data == "admin_stats", IsAdmin())
async def admin_stats(callback: CallbackQuery):
    await callback.answer()
    total_users = await get_user_count()
    text = f"📊 Статистика:\n\n👥 Всего пользователей: {total_users}"
    await callback.message.edit_text(text, reply_markup=admin_back_kb)

@router.callback_query(F.data == "admin_mailing", IsAdmin())
async def admin_mailing_start(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.edit_text("📝 Введи текст рассылки. Он будет отправлен ВСЕМ пользователям.\n\nДля отмены нажми кнопку ниже:", reply_markup=admin_cancel_kb)
    await state.set_state(AdminStates.waiting_mailing_text)

@router.message(AdminStates.waiting_mailing_text, IsAdmin())
async def send_mailing(message: Message, state: FSMContext, bot: Bot):
    text = message.text
    users = await get_all_users_id()
    success = 0
    fail = 0
    
    if not users:
        await message.answer("❌ Нет пользователей в базе для рассылки!", reply_markup=admin_back_kb)
        await state.clear()
        return
    
    await message.answer(f"🚀 Начинаю рассылку {len(users)} пользователям...")
    
    for uid in users:
        try:
            await bot.send_message(uid, text)
            success += 1
            await asyncio.sleep(0.05)  # Защита от лимитов Telegram
        except Exception as e:
            fail += 1
            # Можно логировать ошибки, но не засоряем чат админа
            
    result_text = f"✅ Рассылка завершена!\n\n✅ Успешно отправлено: {success}\n❌ Не доставлено (бот заблокирован или ошибка): {fail}"
    await message.answer(result_text, reply_markup=admin_back_kb)
    await state.clear()

@router.callback_query(F.data == "admin_users", IsAdmin())
async def admin_users(callback: CallbackQuery):
    await callback.answer()
    users = await get_all_users_info()
    if not users:
        await callback.message.edit_text("❌ Нет пользователей в базе.", reply_markup=admin_back_kb)
        return
    
    text = "👥 Список пользователей (первые 10):\n\n"
    for i, (user_id, username, first_name, last_name) in enumerate(users[:10]):
        # Формируем отображение имени
        name_parts = []
        if first_name:
            name_parts.append(first_name)
        if last_name:
            name_parts.append(last_name)
        name = " ".join(name_parts) if name_parts else "Без имени"
        
        # Формируем никнейм с @
        nickname = f"@{username}" if username else "никнейм"
        
        text += f"• {name} - {nickname}\n  <code>{user_id}</code>\n\n"
    
    if len(users) > 10:
        text += f"... и ещё {len(users)-10} пользователей."
    
    await callback.message.edit_text(text, parse_mode="HTML", reply_markup=admin_back_kb)

@router.callback_query(F.data == "admin_back", IsAdmin())
async def admin_back(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.clear()
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 Статистика", callback_data="admin_stats")],
        [InlineKeyboardButton(text="📢 Рассылка", callback_data="admin_mailing")],
        [InlineKeyboardButton(text="👥 Список пользователей", callback_data="admin_users")]
    ])
    await callback.message.edit_text("🔐 Админ-панель", reply_markup=kb)

@router.callback_query(F.data == "admin_cancel", IsAdmin())
async def admin_cancel(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.clear()
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 Статистика", callback_data="admin_stats")],
        [InlineKeyboardButton(text="📢 Рассылка", callback_data="admin_mailing")],
        [InlineKeyboardButton(text="👥 Список пользователей", callback_data="admin_users")]
    ])
    await callback.message.edit_text("❌ Действие отменено\n\n🔐 Админ-панель", reply_markup=kb)

@router.callback_query(F.data == "main_menu", IsAdmin())
async def main_menu(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.clear()
    await callback.message.edit_text("🏠 <b>Главное меню</b>\n\nВыберите действие ниже:\n📊 Калькулятор - расчёт энергопотребления\n❓ Помощь - поддержка\nℹ️ О боте - информация\n\n🎯 Начните с калькулятора для расчётов!", 
                                   parse_mode="HTML", reply_markup=calculator_kb)


@router.message(F.text == "Отмена", AdminStates.waiting_mailing_text, IsAdmin())
@router.message(Command("cancel"), AdminStates.waiting_mailing_text, IsAdmin())
async def cancel_mailing(message: Message, state: FSMContext):
    await state.clear()
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 Статистика", callback_data="admin_stats")],
        [InlineKeyboardButton(text="📢 Рассылка", callback_data="admin_mailing")],
        [InlineKeyboardButton(text="👥 Список пользователей", callback_data="admin_users")]
    ])
    await message.answer("❌ Рассылка отменена\n\n🔐 Админ-панель", reply_markup=kb)
