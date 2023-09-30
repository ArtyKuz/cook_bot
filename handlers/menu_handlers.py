from aiogram import Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from FSM import FSM
from keyboards.keyboards import create_pagination_kb
from services.services import add_user_in_db, get_favorites_dishes

router = Router()


# Этот хэндлер будет срабатывать на команду "/start"
@router.message(Command(commands=["start"]), StateFilter(default_state))
@router.message(Command(commands=["start"]), ~StateFilter(default_state))
async def process_start_command(message: Message, state: FSMContext, session: AsyncSession):
    await add_user_in_db(message.from_user.id, message.from_user.username, session)
    await state.set_state(FSM.find_dishes)
    await message.answer(f'Привет {message.from_user.first_name}!\n\nЭто кулинарный бот!\n'
                         f'Напиши мне название любого блюда и я найду '
                         'для тебя несколько рецептов для его приготовления!')


# Этот хэндлер будет срабатывать на команду "/favorites"
@router.message(Command(commands=['favorites']), StateFilter(default_state))
@router.message(Command(commands=['favorites']), ~StateFilter(default_state))
async def process_favorite_command(message: Message, state: FSMContext, session: AsyncSession):
    data = await state.get_data()
    favorites_dishes: dict = await get_favorites_dishes(message.from_user.id, session)
    data['favorites_dishes'] = favorites_dishes
    data['page'] = 1
    await state.update_data(data)
    await state.set_state(FSM.favorites)
    await message.answer(f'Ваши избранные рецепты ❤',
                         reply_markup=create_pagination_kb(1, data['page'],
                                                           favorites_dishes,
                                                           'Вернуться к поиску других блюд 🍲',
                                                           ))


# Этот хэндлер будет срабатывать на команду "/help"
@router.message(Command(commands=['help']), StateFilter(default_state))
@router.message(Command(commands=['help']), ~StateFilter(default_state))
async def process_help_command(message: Message, state: FSMContext):
    await state.set_state(FSM.find_dishes)
    await message.answer('Напиши боту название любого кулинарного блюда и он найдет для тебя несколько рецептов!')



