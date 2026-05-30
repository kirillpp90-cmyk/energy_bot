from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command

router = Router()

@router.message(F.text == 'ℹ️ О боте')
@router.message(Command('about'))
async def about(message: Message):
    await message.answer(f'ℹ️ <b>Бот-калькулятор энергопотребления</b>\n\n'
                         '🔋 Версия 1.0\n\n'
                         "Ссылка на репозиторий — <a href='tg://user?id=123456789'>Кирилл</a>, <a href='tg://user?id=987654321'>Дмитрий</a>\n\n"
                         '👨‍💻 Авторы: <a href="https://t.me/sherek008">Кирилл</a>, <a href="https://t.me/@zvsee">Дмитрий</a>\n\n'
                         '📋 <b>Доступные команды:</b>\n'
                         '/start - Начать работу\n'
                         '/calc - Калькулятор\n'
                         '/about - О боте\n'
                         '/menu - Главное меню\n'
                         '/help - Помощь\n\n'
                         '🎯 Рассчитайте энергопотребление ваших приборов!', parse_mode='HTML')
