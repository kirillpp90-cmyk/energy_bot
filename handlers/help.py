from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.filters import Command

from keyboards import cancel_kb, calculator_kb
from states import HelpState
from admin import admin_ids

router = Router()

@router.message(F.text == '❓ Помощь')
@router.message(Command('help'))
async def help_def(message: Message, state: FSMContext):
    await message.answer('📝 Опишите вашу проблему, и я помогу вам! \n\nВаше сообщение будет отправлено администратору для решения.', reply_markup=cancel_kb)
    await state.set_state(HelpState.waiting_question)

@router.message(HelpState.waiting_question)
async def process_question(message: Message, state: FSMContext, bot: Bot):
    msg = message.text
    id_user = message.from_user.id
    username_user = message.from_user.username
    await bot.send_message(admin_ids[0], f"📨 Новое сообщение в поддержку!\n\n👤 Пользователь: {id_user} (@{username_user})\n\n💬 Сообщение:\n{msg}")
    await state.clear()
    await message.answer("✅ Ваше сообщение успешно отправлено в поддержку! 🎯\n\nМы свяжемся с вами в ближайшее время. 💙", reply_markup=calculator_kb)
