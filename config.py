import os

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import Redis, RedisStorage
from dotenv import load_dotenv

load_dotenv()

token: str = os.getenv('TOKEN')
bot = Bot(token=token, parse_mode='HTML')
# Инициализируем Redis
redis: Redis = Redis(host='localhost', db=1)

storage: RedisStorage = RedisStorage(redis=redis)

dp: Dispatcher = Dispatcher(storage=storage)