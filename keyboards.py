from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

cancel_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Отмена")]],
    resize_keyboard=True
)

calculator_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='📊 Калькулятор')],
        [KeyboardButton(text='ℹ️ О боте'), KeyboardButton(text='❓ Помощь')]
    ],
    resize_keyboard=True
)
