from aiogram import Router
from aiogram.filters import Command, StateFilter
from aiogram.types import Message
from aiogram.fsm.state import default_state
from aiogram.filters.state import State
from aiogram.fsm.context import FSMContext
from FSM import FSM

router = Router()

# Этот хэндлер будет срабатывать на команду "/start"
@router.message(Command(commands=["start"]), StateFilter(default_state))
@router.message(Command(commands=["start"]), ~StateFilter(default_state))
async def process_start_command(message: Message, state: FSMContext):
    await message.answer(f'Привет {message.from_user.first_name}!\n\nЭто кулинарный бот!\n'
                         f'Напиши мне название любого блюда и я найду '
                         'для тебя несколько рецептов для его приготовления!')
    await state.set_state(FSM.find_dishes)


# Этот хэндлер будет срабатывать на команду "/help"
@router.message(Command(commands=['help']), StateFilter(default_state))
@router.message(Command(commands=['help']), ~StateFilter(default_state))
async def process_help_command(message: Message):
    await message.answer('Напиши боту название любого кулинарного блюда и он найдет для тебя несколько рецептов!')


