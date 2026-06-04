from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, TelegramObject
from aiogram.filters import Command, BaseFilter
from aiogram.fsm.context import FSMContext

from config import admin_ids
from database import get_user_count, get_all_users_id, get_all_users_info
import asyncio

from keyboards import cancel_kb, admin_back_kb, admin_cancel_kb, calculator_kb
from states import AdminStates

class IsAdmin(BaseFilter):
    async def __call__(self, obj: TelegramObject):
        return obj.from_user.id in admin_ids

router = Router()

USERS_PER_PAGE = 10

def build_admin_panel_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 Статистика", callback_data="admin_stats")],
        [InlineKeyboardButton(text="📢 Рассылка", callback_data="admin_mailing")],
        [InlineKeyboardButton(text="👥 Список пользователей", callback_data="admin_users:0")]
    ])

def build_users_page(users: list, page: int) -> tuple[str, InlineKeyboardMarkup]:
    """Возвращает текст и клавиатуру для страницы пользователей"""
    total = len(users)
    total_pages = (total - 1) // USERS_PER_PAGE + 1
    start = page * USERS_PER_PAGE
    end = start + USERS_PER_PAGE
    page_users = users[start:end]

    text = f"👥 Пользователи (стр. {page + 1}/{total_pages}, всего {total}):\n\n"
    for user_id, username, first_name, last_name in page_users:
        name_parts = []
        if first_name:
            name_parts.append(first_name)
        if last_name:
            name_parts.append(last_name)
        name = " ".join(name_parts) if name_parts else "Без имени"
        nickname = f"@{username}" if username else "без никнейма"
        text += f"• {name} — {nickname}\n  <code>{user_id}</code>\n\n"

    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton(text="◀️ Назад", callback_data=f"admin_users:{page - 1}"))
    if end < total:
        nav_buttons.append(InlineKeyboardButton(text="Вперёд ▶️", callback_data=f"admin_users:{page + 1}"))

    kb_rows = []
    if nav_buttons:
        kb_rows.append(nav_buttons)
    kb_rows.append([InlineKeyboardButton(text="🔙 Назад в админ-панель", callback_data="admin_back")])

    return text, InlineKeyboardMarkup(inline_keyboard=kb_rows)

@router.message(Command("admin"), IsAdmin())
async def admin_panel(message: Message):
    await message.answer("🔐 Админ-панель", reply_markup=build_admin_panel_kb())

@router.callback_query(F.data == "admin_stats", IsAdmin())
async def admin_stats(callback: CallbackQuery):
    await callback.answer()
    total_users = await get_user_count()
    text = f"📊 Статистика:\n\n👥 Всего пользователей: {total_users}"
    await callback.message.edit_text(text, reply_markup=admin_back_kb)

@router.callback_query(F.data == "admin_mailing", IsAdmin())
async def admin_mailing_start(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.edit_text(
        "📝 Введи текст рассылки. Он будет отправлен ВСЕМ пользователям.\n\nДля отмены нажми кнопку ниже:",
        reply_markup=admin_cancel_kb
    )
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
            await asyncio.sleep(0.05)
        except Exception:
            fail += 1

    result_text = (
        f"✅ Рассылка завершена!\n\n"
        f"✅ Успешно отправлено: {success}\n"
        f"❌ Не доставлено: {fail}"
    )
    await message.answer(result_text, reply_markup=admin_back_kb)
    await state.clear()

@router.callback_query(F.data.startswith("admin_users:"), IsAdmin())
async def admin_users(callback: CallbackQuery):
    await callback.answer()

    page = int(callback.data.split(":")[1])

    users = await get_all_users_info()
    if not users:
        await callback.message.edit_text("❌ Нет пользователей в базе.", reply_markup=admin_back_kb)
        return

    total_pages = (len(users) - 1) // USERS_PER_PAGE + 1

    if page < 0:
        page = 0
    if page >= total_pages:
        page = total_pages - 1

    text, kb = build_users_page(users, page)
    await callback.message.edit_text(text, parse_mode="HTML", reply_markup=kb)

@router.callback_query(F.data == "admin_back", IsAdmin())
async def admin_back(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.clear()
    await callback.message.edit_text("🔐 Админ-панель", reply_markup=build_admin_panel_kb())

@router.callback_query(F.data == "admin_cancel", IsAdmin())
async def admin_cancel(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.clear()
    await callback.message.edit_text("❌ Действие отменено\n\n🔐 Админ-панель", reply_markup=build_admin_panel_kb())

@router.callback_query(F.data == "main_menu", IsAdmin())
async def main_menu_admin(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.clear()
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer(
        "🏠 Вы в главном меню",
        reply_markup=calculator_kb
    )

@router.message(F.text == "Отмена", AdminStates.waiting_mailing_text, IsAdmin())
@router.message(Command("cancel"), AdminStates.waiting_mailing_text, IsAdmin())
async def cancel_mailing(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("❌ Рассылка отменена\n\n🔐 Админ-панель", reply_markup=build_admin_panel_kb())