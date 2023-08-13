from aiogram.filters.state import State, StatesGroup


class FSM(StatesGroup):
    find_dishes = State()
    get_recipe = State()
