import asyncio
import os

import asyncpg
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import Redis, RedisStorage
from aiogram.types import BotCommand
from dotenv import load_dotenv

from handlers import menu_handlers, user_handlers
from middlewares.middlewares import DBMiddleware
from config import bot, dp


async def main():

    dp.include_router(menu_handlers.router)
    dp.include_router(user_handlers.router)

    # Создаем список с командами и их описанием для кнопки menu
    main_menu_commands = [
        BotCommand(command='/start',
                   description='Запустить бота'),
        BotCommand(command='/favorites',
                   description='Избранные рецепты'),
        BotCommand(command='/help',
                   description='Помощь'),
       ]

    await bot.set_my_commands(main_menu_commands)
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
    asyncio.run(main())
