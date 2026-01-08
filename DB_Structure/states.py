from aiogram.fsm.state import State, StatesGroup
class RegisterUser(StatesGroup):
    first_name = State()
    last_name = State()
    direction = State()
    experience = State()
    duty = State()
    confirm = State()

