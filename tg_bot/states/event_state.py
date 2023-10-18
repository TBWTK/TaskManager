from aiogram.fsm.state import State, StatesGroup


class FSMFillFormEvent(StatesGroup):
    event_or_task = State()

    close = State()

    project = State()
    responsible = State()

    time = State()
    date = State()
    description = State()
    notification = State()
