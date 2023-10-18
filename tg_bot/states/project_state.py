from aiogram.fsm.state import State, StatesGroup


class FSMFillFormProject(StatesGroup):
    creating_or_viewing = State()
    create_name_project = State()

    viewing = State()
    viewing_admin = State()
    viewing_responsible = State()

    final_choice = State()
