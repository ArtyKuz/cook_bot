import asyncpg.connection
from aiogram import Router
from aiogram.filters import Command, StateFilter
from aiogram.types import Message
from aiogram.fsm.state import default_state
from aiogram.filters.state import State
from aiogram.fsm.context import FSMContext
from FSM import FSM

from keyboards.keyboards import create_kb
from services.services import add_user_in_db, get_favorites_dishes

router = Router()


# Этот хэндлер будет срабатывать на команду "/start"
@router.message(Command(commands=["start"]), StateFilter(default_state))
@router.message(Command(commands=["start"]), ~StateFilter(default_state))
async def process_start_command(message: Message, state: FSMContext, conn: asyncpg.connection.Connection):
    await add_user_in_db(message.from_user.id, message.from_user.username, conn)
    await state.set_state(FSM.find_dishes)
    await message.answer(f'Привет {message.from_user.first_name}!\n\nЭто кулинарный бот!\n'
                         f'Напиши мне название любого блюда и я найду '
                         'для тебя несколько рецептов для его приготовления!')


# Этот хэндлер будет срабатывать на команду "/favorites"
@router.message(Command(commands=['favorites']), StateFilter(default_state))
@router.message(Command(commands=['favorites']), ~StateFilter(default_state))
async def process_favorite_command(message: Message, state: FSMContext, conn: asyncpg.connection.Connection):
    data = await state.get_data()
    favorites_dishes: dict = await get_favorites_dishes(message.from_user.id, conn)
    data['favorites_dishes'] = favorites_dishes
    await state.update_data(data)
    await state.set_state(FSM.favorites)
    await message.answer(f'Ваши избранные рецепты ❤',
                         reply_markup=create_kb(1, 'Вернуться к поиску других блюд 🍲', **favorites_dishes))


# Этот хэндлер будет срабатывать на команду "/help"
@router.message(Command(commands=['help']), StateFilter(default_state))
@router.message(Command(commands=['help']), ~StateFilter(default_state))
async def process_help_command(message: Message):
    await message.answer('Напиши боту название любого кулинарного блюда и он найдет для тебя несколько рецептов!')



