from unittest.mock import AsyncMock

import pytest
from aiogram import Dispatcher
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey
from aiogram.methods import SendMessage

from handlers.menu_handlers import process_help_command, process_start_command
from tests.utils import TEST_USER, TEST_USER_CHAT, get_message, get_update


@pytest.mark.asyncio
async def test_start_handler(dispatcher: Dispatcher, storage, bot, connection):
    message = AsyncMock()
    # result = await dispatcher.feed_update(bot=bot, update=get_update(message=get_message(text='/start')))
    state = FSMContext(
        bot=bot,
        storage=storage,
        key=StorageKey(bot_id=bot.id, user_id=TEST_USER.id, chat_id=TEST_USER_CHAT.id)
    )
    await process_start_command(message, state, connection)
    assert await state.get_state() == 'FSM:find_dishes'
    message.answer.assert_called_with(f'Привет {message.from_user.first_name}!\n\nЭто кулинарный бот!\n'
                                      f'Напиши мне название любого блюда и я найду '
                                      'для тебя несколько рецептов для его приготовления!')
    # assert result.text == f'Привет {TEST_USER.first_name}!\n\nЭто кулинарный бот!\n' \
    #                       f'Напиши мне название любого блюда и я найду ' \
    #                       f'для тебя несколько рецептов для его приготовления!'


@pytest.mark.asyncio
async def test_help_handler(storage, bot):
    message = AsyncMock()
    state = FSMContext(
        bot=bot,
        storage=storage,
        key=StorageKey(bot_id=bot.id, user_id=TEST_USER.id, chat_id=TEST_USER_CHAT.id)
    )
    await process_help_command(message, state)
    assert await state.get_state() == 'FSM:find_dishes'
    message.answer.assert_called_with('Напиши боту название любого кулинарного блюда и он найдет для тебя '
                                      'несколько рецептов!')