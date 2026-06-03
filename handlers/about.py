from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command

router = Router()

@router.message(F.text == 'ℹ️ О боте')
@router.message(Command('about'))
async def about(message: Message):
    await message.answer(
        'ℹ️ <b>Бот-калькулятор энергопотребления</b>\n\n'
        '🔋 Версия 1.1\n\n'
        "🔗 Репозиторий: <a href='https://github.com/kirillpp90-cmyk/energy_bot'>energy_bot на GitHub</a>\n\n"
        "👨‍💻 Авторы: "
        "<a href='tg://user?id=5548414556'>Кирилл</a>, "
        "<a href='https://t.me/zvsee'>Дмитрий</a>\n\n"
        '📋 <b>Доступные команды:</b>\n'
        '/start — начать работу\n'
        '/calc — точный расчёт (ручной ввод)\n'
        '/quick — быстрый расчёт по типу жилья\n'
        '/tariff — посмотреть текущий тариф\n'
        '/set_tariff — изменить тариф\n'
        '/mydevices — мои сохранённые приборы\n'
        '/menu — главное меню\n'
        '/help — написать в поддержку\n'
        '/about — о боте\n\n'
        '⚡ <b>Режимы расчёта:</b>\n'
        '• <b>Быстрый</b> — выбери тип жилья, получи оценку\n'
        '• <b>Точный</b> — введи параметры прибора вручную\n\n'
        '🎯 Рассчитайте энергопотребление ваших приборов!',
        parse_mode='HTML'
    )
