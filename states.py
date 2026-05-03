from aiogram.fsm.state import State, StatesGroup

class CalcState(StatesGroup):
    waiting_power = State()
    waiting_hours = State()
    waiting_days = State()
    waiting_tariff = State()

class HelpState(StatesGroup):
    waiting_question = State()

