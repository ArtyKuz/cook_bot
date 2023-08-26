import os

import asyncpg
from aiogram import Bot, Dispatcher
import asyncio

from aiogram.types import BotCommand

from middlewares.middlewares import DBMiddleware
from services.services import get_recipe, get_list_of_dishes
from aiogram.fsm.storage.redis import RedisStorage, Redis
# from aiogram.fsm.storage.memory import MemoryStorage
from handlers import menu_handlers, user_handlers
from dotenv import load_dotenv


async def main():
    load_dotenv()

    token: str = os.getenv('TOKEN')

    bot = Bot(token=token, parse_mode='HTML')
    # Инициализируем Redis
    redis: Redis = Redis(host='localhost', db=1)

    storage: RedisStorage = RedisStorage(redis=redis)
    # storage: MemoryStorage = MemoryStorage()

    dp: Dispatcher = Dispatcher(storage=storage)

    dp.include_router(menu_handlers.router)
    dp.include_router(user_handlers.router)


    # async def set_main_menu(bot: Bot):

        # Создаем список с командами и их описанием для кнопки menu
    main_menu_commands = [
        BotCommand(command='/start',
                   description='Запустить бота'),
        BotCommand(command='/favorites',
                   description='Избранные рецепты'),
        BotCommand(command='/help',
                   description='Помощь'),
       ]

    # await bot.set_my_commands(main_menu_commands)

    await bot.set_my_commands(main_menu_commands)
    # async def create_pool(dp: Dispatcher):
    pool = await asyncpg.create_pool(database=os.getenv('DATABASE'),
                                     user=os.getenv('USER'),
                                     password=os.getenv('PASSWORD'),
                                     host=os.getenv('HOST'),
                                     port=os.getenv('PORT'))
    db_middleware = DBMiddleware(pool)
    # Добавляем мидлвари в диспетчер
    dp.update.middleware(db_middleware)
    await dp.start_polling(bot)

if __name__ == '__main__':
    # loop = asyncio.get_event_loop()
    # loop.run_until_complete(create_pool(dp))
    # Регистрируем асинхронную функцию в диспетчере,
    # которая будет выполняться на старте бота,
    # dp.startup.register(set_main_menu)
    # dp.run_polling(bot)
    asyncio.run(main())
