from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

cancel_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Отмена")]],
    resize_keyboard=True
)

calculator_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='📊 Калькулятор'), KeyboardButton(text='📱 Приборы')],
        [KeyboardButton(text='ℹ️ О боте'), KeyboardButton(text='❓ Помощь')],
        [KeyboardButton(text='⚡ Быстрый расчёт')]
    ],
    resize_keyboard=True
)

admin_back_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Назад в админ-панель", callback_data="admin_back")],
        [InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")]
    ]
)

admin_cancel_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="❌ Отмена", callback_data="admin_cancel")],
        [InlineKeyboardButton(text="🔙 Назад в админ-панель", callback_data="admin_back")]
    ]
)


save_after_calc_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="💾 Сохранить прибор", callback_data='save_from_calc')],
        [InlineKeyboardButton(text="🔄 Новый расчет", callback_data="new_calc")],
        [InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")]
    ]
)

quick_calc_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='1-ая комнатная квартира', callback_data='quick_1room')],
        [InlineKeyboardButton(text='2-ая комнатная квартира', callback_data='quick_2room')],
        [InlineKeyboardButton(text='3-ая комнатная квартира', callback_data='quick_3room')],
        [InlineKeyboardButton(text='Дом', callback_data='quick_house')],
    ]
)
