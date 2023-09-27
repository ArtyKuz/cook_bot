import asyncio
import os

import asyncpg
import pytest
import pytest_asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv

from mocked_bot import MockedBot


@pytest_asyncio.fixture(scope="session")
async def storage():
    tmp_storage = MemoryStorage()
    try:
        yield tmp_storage
    finally:
        await tmp_storage.close()


@pytest.fixture()
def bot():
    bot = MockedBot()
    token = Bot.set_current(bot)
    try:
        yield bot
    finally:
        Bot.reset_current(token)


@pytest_asyncio.fixture()
async def dispatcher():
    dp = Dispatcher()
    await dp.emit_startup()
    try:
        yield dp
    finally:
        await dp.emit_shutdown()


@pytest.fixture(scope="session")
def event_loop():
    return asyncio.get_event_loop()


@pytest_asyncio.fixture(scope="session")
async def session_maker():
    # Определяем путь к файлу с переменными окружения
    env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
    # Загружаем переменные окружения из файла
    load_dotenv(env_path)

    pool = await asyncpg.create_pool(database=os.getenv('DATABASE'),
                                     user=os.getenv('USER'),
                                     password=os.getenv('PASSWORD'),
                                     host=os.getenv('HOST'),
                                     port=os.getenv('PORT'))
    conn: asyncpg.connection.Connection = await pool.acquire()
    try:
        yield conn
    finally:
        await conn.close()