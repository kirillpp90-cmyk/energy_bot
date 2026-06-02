from aiogram.fsm.state import State, StatesGroup

class CalcState(StatesGroup):
    waiting_power = State()
    waiting_hours = State()
    waiting_days = State()
    waiting_device_name = State()

class HelpState(StatesGroup):
    waiting_question = State()

class AdminStates(StatesGroup):
    waiting_mailing_text = State()

class TariffState(StatesGroup):
    waiting_tariff_value = State()