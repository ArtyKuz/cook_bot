import asyncpg.connection
from aiogram import Router, F
from aiogram.filters import Command, Text, StateFilter
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from FSM import FSM
from aiogram.fsm.state import default_state
from services.services import get_list_of_dishes, get_recipe, add_dish_to_favorites, get_favorite_recipe, delete_recipe
from keyboards.keyboards import create_kb


router = Router()


@router.callback_query(Text(text=['Выбрать другое блюдо 🍲',
                            'Вернуться к поиску других блюд 🍲']), ~StateFilter(default_state))
async def select_dishes(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.clear()
    await state.set_state(FSM.find_dishes)
    await callback.message.edit_text('Напиши мне название любого блюда и я найду '
                         'для тебя несколько рецептов для его приготовления!')



@router.callback_query(Text(text='Выбрать другой рецепт 📃'), ~StateFilter(default_state))
async def back_dishes(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    data = await state.get_data()
    await callback.message.edit_text('Вот что мне удалось найти!',
                                     reply_markup=create_kb(1, 'Выбрать другое блюдо 🍲', **data['titles']))


@router.message(StateFilter(FSM.find_dishes))
async def list_of_dishes(message: Message, state: FSMContext):
    data = await get_list_of_dishes(message.text)
    if data:
        await state.update_data(data)
        await message.answer('Вот что мне удалось найти!',
                             reply_markup=create_kb(1, 'Выбрать другое блюдо 🍲', **data['titles']))
        await state.set_state(FSM.get_recipe)
    else:
        await message.answer('К сожалению по данному запросу ничего не найдено, попробуйте еще раз...')
        await state.set_state(FSM.find_dishes)


@router.callback_query(StateFilter(FSM.get_recipe), Text(text='Добавить в избранное ❤'))
async def add_to_favorites(callback: CallbackQuery, state: FSMContext, conn: asyncpg.connection.Connection):
    await callback.answer()
    data = await state.get_data()
    result = await add_dish_to_favorites(callback.from_user.id, data['current_dish'],  data['recipe'], conn)
    if result:
        await callback.message.answer('Рецепт успешно добавлен в избранное!',
                                      reply_markup=create_kb(1, 'Выбрать другой рецепт 📃',
                                                             'Выбрать другое блюдо 🍲'))
    else:
        await callback.message.answer('Данный рецепт уже находится в списке ваших избранных рецептов!',
                                      reply_markup=create_kb(1, 'Выбрать другой рецепт 📃',
                                                             'Выбрать другое блюдо 🍲'))


@router.callback_query(StateFilter(FSM.get_recipe))
async def recipe(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    data = await state.get_data()
    recipe = await get_recipe(data['dishes'].get(callback.data))
    data['recipe'] = recipe
    data['current_dish'] = data['titles'][callback.data]
    await state.update_data(data)
    if recipe:
        await callback.message.edit_text(f'{recipe}', reply_markup=create_kb(1, 'Выбрать другой рецепт 📃',
                                                                             'Добавить в избранное ❤'))
    else:
        await callback.message.edit_text('К сожалению произошла ошибка... Попробуйте выбрать другой рецепт',
                             reply_markup=create_kb(1, 'Выбрать другое блюдо 🍲', **data['titles']))


@router.callback_query(StateFilter(FSM.favorites), Text(text='Избранные рецепты ❤'))
async def all_favorites(callback: CallbackQuery, state: FSMContext, conn: asyncpg.connection.Connection):
    await callback.answer()
    data = await state.get_data()
    favorites_dishes = data['favorites_dishes']
    await callback.message.answer(f'Ваши избранные рецепты ❤',
                         reply_markup=create_kb(1, 'Вернуться к поиску других блюд 🍲', **favorites_dishes))


@router.callback_query(StateFilter(FSM.favorites), Text(text='Удалить рецепт из избранных 🗑'))
async def delete_recipe_handler(callback: CallbackQuery, state: FSMContext, conn: asyncpg.connection.Connection):
    data = await state.get_data()
    data = await delete_recipe(callback.from_user.id, data, conn)
    await state.update_data(data)
    await callback.message.edit_text('Рецепт удален из списка избранных!',
                                     reply_markup=create_kb(1,
                                                            'Избранные рецепты ❤',
                                                            'Вернуться к поиску других блюд 🍲'))


@router.callback_query(StateFilter(FSM.favorites))
async def favorite_recipe(callback: CallbackQuery, state: FSMContext, conn: asyncpg.connection.Connection):
    await callback.answer()
    data = await state.get_data()
    data['favorite_dish_id'] = callback.data
    await state.update_data(data)
    recipe = await get_favorite_recipe(callback.data, conn)
    await callback.message.edit_text(recipe,
                                     reply_markup=create_kb(1,
                                                            'Удалить рецепт из избранных 🗑',
                                                            'Избранные рецепты ❤'))








