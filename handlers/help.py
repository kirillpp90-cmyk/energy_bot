from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.filters import Command

from keyboards import cancel_kb, calculator_kb
from states import HelpState
from config import admin_ids

router = Router()

@router.message(F.text == '❓ Помощь')
@router.message(Command('help'))
async def help_def(message: Message, state: FSMContext):
    await message.answer(
        '📝 Опишите вашу проблему. Вы можете отправить текст, фото, видео, документ или GIF.\n\n'
        'Ваше сообщение будет отправлено администратору.',
        reply_markup=cancel_kb
    )
    await state.set_state(HelpState.waiting_question)


@router.message(HelpState.waiting_question)
async def process_question(message: Message, state: FSMContext, bot: Bot):
    user_id = message.from_user.id
    username = message.from_user.username or "нет username"

    if not admin_ids:
        await message.answer("❌ Администраторы не настроены.", reply_markup=calculator_kb)
        await state.clear()
        return

    admin_id = admin_ids[0]

    # Информация о пользователе
    await bot.send_message(
        admin_id,
        f"📨 Новое сообщение в поддержку!\n\n"
        f"👤 ID: {user_id}\n"
        f"👤 Username: @{username}"
    )

    # Копируем любое сообщение (поддерживает фото, видео, гифки, документы)
    try:
        await bot.copy_message(
            chat_id=admin_id,
            from_chat_id=user_id,
            message_id=message.message_id
        )
        await message.answer("✅ Сообщение отправлено в поддержку!", reply_markup=calculator_kb)
    except Exception as e:
        await message.answer("❌ Не удалось отправить.", reply_markup=calculator_kb)
        print(f"Ошибка пересылки: {e}")

    await state.clear()
