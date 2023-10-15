from aiogram.fsm.state import State, StatesGroup


class FSMFillFormName(StatesGroup):
    first_name = State()
    last_name = State()
