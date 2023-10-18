from aiogram.fsm.state import State, StatesGroup


class FSMFillFormNotif(StatesGroup):
    time = State()
    date = State()
