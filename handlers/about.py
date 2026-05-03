from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command

router = Router()

@router.message(F.text == 'ℹ️ О боте')
@router.message(Command('about'))
async def about(message: Message):
    await message.answer(f'ℹ️ Бот-калькулятор энергопотребления\n\n'
                         'Версия 1.0\n\n'
                         f'Автор: <a href="https://t.me/sherek008">{message.from_user.full_name}</a>\n'
                         'Команды: /start, /calc, /about, /menu, /help', parse_mode='HTML')
