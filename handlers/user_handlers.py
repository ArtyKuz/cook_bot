import os

import asyncpg.connection
from aiogram import F, Router, types
from aiogram.filters import Command, StateFilter, Text
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import (CallbackQuery, ContentType, Message,
                           ReplyKeyboardRemove)
from dotenv import load_dotenv

from config import bot
from FSM import FSM
from keyboards.keyboards import create_kb, create_pagination_kb
from services.services import (add_dish_to_favorites, check_count_recipes,
                               delete_recipe, get_favorite_recipe,
                               get_list_of_dishes, get_premium, get_recipe)

load_dotenv()
router = Router()

# buy
@router.callback_query(~StateFilter(default_state), Text(text='Оформить Premium доступ 💎'))
async def buy(callback: CallbackQuery):
    await callback.answer()
    PRICE = types.LabeledPrice(label="Premium доступ", amount=100 * 100)  # в копейках (руб)
    await bot.send_invoice(callback.message.chat.id,
                           title="Активация Premium доступа",
                           description="После оплаты Premium доступ будет действовать бессрочно.",
                           provider_token=os.getenv('PAYMENTS_TOKEN'),
                           currency="rub",
                           is_flexible=False,
                           prices=[PRICE],
                           start_parameter="subscription",
                           payload="test-invoice-payload")


@router.pre_checkout_query(lambda query: True)
async def pre_checkout_query(pre_checkout_q: types.PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_q.id, ok=True)


# successful payment
@router.message(F.successful_payment)
async def successful_payment(message: types.Message, conn: asyncpg.connection.Connection):
    await get_premium(message.from_user.id, conn)
    await message.answer(f"<b>Premium</b> доступ успешно активирован!!!\n\n"
                         f"Теперь вы можете добавлять не ограниченное количество рецептов в избранное!",
                         reply_markup=create_kb(1, 'Вернуться к рецептам 📃',
                                                   'Выбрать другое блюдо 🍲'))


@router.callback_query(Text(text=['Выбрать другое блюдо 🍲',
                            'Вернуться к поиску других блюд 🍲']), ~StateFilter(default_state))
async def select_dishes(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.clear()
    await state.set_state(FSM.find_dishes)
    await callback.message.edit_text('Напиши мне название любого блюда и я найду '
                         'для тебя несколько рецептов для его приготовления!')



@router.callback_query(Text(text=['Выбрать другой рецепт 📃',
                            'Вернуться к рецептам 📃']), ~StateFilter(default_state))
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
    if await check_count_recipes(callback.from_user.id, conn):
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
    else:
        await callback.message.answer('Вы не можете добавлять в избранное более 10-ти рецептов, '
                                      'чтобы добавлять неограниченное количество рецептов в избранное оформите '
                                      '<b>Premium доступ!</b>',
                                      reply_markup=create_kb(1, 'Оформить Premium доступ 💎',
                                                             'Выбрать другой рецепт 📃',
                                                             'Выбрать другое блюдо 🍲'))


@router.callback_query(StateFilter(FSM.get_recipe))
async def recipe(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    data = await state.get_data()
    recipe = await get_recipe(data['dishes'].get(callback.data), data['titles'].get(callback.data))
    data['recipe'] = recipe
    data['current_dish'] = data['titles'][callback.data]
    await state.update_data(data)
    if recipe:
        await callback.message.edit_text(f'{recipe}', reply_markup=create_kb(1, 'Выбрать другой рецепт 📃',
                                                                             'Добавить в избранное ❤'))
    else:
        await callback.message.edit_text('К сожалению произошла ошибка... Попробуйте выбрать другой рецепт',
                             reply_markup=create_kb(1, 'Выбрать другое блюдо 🍲', **data['titles']))


@router.callback_query(StateFilter(FSM.favorites), Text(text=['Избранные рецепты ❤',
                                                        'back',
                                                        'forward']))
async def all_favorites(callback: CallbackQuery, state: FSMContext, conn: asyncpg.connection.Connection):
    await callback.answer()
    data = await state.get_data()
    favorites_dishes = data['favorites_dishes']
    if callback.data in ['back', 'forward']:
        data['page'] = data['page'] - 1 if callback.data == 'back' else data['page'] + 1
    page = data['page']
    await state.update_data(data)
    await callback.message.edit_text(f'Ваши избранные рецепты ❤',
                         reply_markup=create_pagination_kb(1, page, favorites_dishes,
                                                           'Вернуться к поиску других блюд 🍲'))


@router.callback_query(StateFilter(FSM.favorites), Text(text='Удалить рецепт из избранных 🗑'))
async def delete_recipe_handler(callback: CallbackQuery, state: FSMContext, conn: asyncpg.connection.Connection):
    data = await state.get_data()
    await delete_recipe(callback.from_user.id, data, conn)
    # await state.update_data(data)
    await callback.message.edit_text('Рецепт удален из списка избранных!\n\n'
                                     'Вернуться к избранным рецептам - \n/favorites',
                                     reply_markup=create_kb(1,
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







