from aiogram import Router, F
from aiogram.filters import Command, Text, StateFilter
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from FSM import FSM
from aiogram.fsm.state import default_state
from services.services import get_list_of_dishes, get_recipe
from keyboards.keyboards import create_kb


router = Router()


@router.message(F.text == 'Выбрать другое блюдо 🍲', ~StateFilter(default_state))
async def select_dishes(message: Message, state: FSMContext):
    await state.clear()
    await message.answer('Напиши мне название какого-нибудь блюда и я найду '
                         'для тебя несколько рецептов для его приготовления!', reply_markup=ReplyKeyboardRemove)
    await state.set_state(FSM.find_dishes)


@router.message(F.text == 'Выбрать другой рецепт 📃', ~StateFilter(default_state))
async def back_dishes(message: Message, state: FSMContext):
    data = await state.get_data()
    await message.answer('Вот что мне удалось найти!', reply_markup=create_kb(1, *data, 'Выбрать другое '
                                                                                                      'блюдо 🍲'))


@router.message(StateFilter(FSM.find_dishes))
async def list_of_dishes(message: Message, state: FSMContext):
    dishes = await get_list_of_dishes(message.text)
    if dishes:
        await state.update_data(data=dishes)
        await message.answer('Вот что мне удалось найти!', reply_markup=create_kb(1, *dishes, 'Выбрать другое '
                                                                                                      'блюдо 🍲'))
        await state.set_state(FSM.get_recipe)
    else:
        await message.answer('К сожалению по данному запросу ничего не найдено, попробуйте еще раз...')
        await state.set_state(FSM.find_dishes)



@router.message(StateFilter(FSM.get_recipe))
async def recipe(message: Message, state: FSMContext):
    data = await state.get_data()
    recipe = await get_recipe(data.get(message.text))
    if recipe:
        await message.answer(f'{recipe}', reply_markup=create_kb(1, 'Выбрать другой рецепт 📃'))
    else:
        await message.answer('К сожалению произошла ошибка... Попробуйте выбрать другой рецепт',
                             reply_markup=create_kb(1, *data, 'Выбрать другое блюдо 🍲'))




