from unittest.mock import AsyncMock

import pytest
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey


from handlers.menu_handlers import process_start_command
from tests.utils import TEST_USER, TEST_USER_CHAT


@pytest.mark.asyncio
async def test_start_handler(storage, bot, session_maker):
    message = AsyncMock()
    state = FSMContext(
        bot=bot,
        storage=storage,
        key=StorageKey(bot_id=bot.id, user_id=TEST_USER.id, chat_id=TEST_USER_CHAT.id)
    )
    await process_start_command(message, state, session_maker)
    assert await state.get_state() == 'FSM:find_dishes'
    message.answer.assert_called_with(f'Привет {message.from_user.first_name}!\n\nЭто кулинарный бот!\n'
                                      f'Напиши мне название любого блюда и я найду '
                                      'для тебя несколько рецептов для его приготовления!')
