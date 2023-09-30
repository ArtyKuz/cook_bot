import asyncio
import os

from aiogram.types import BotCommand
from sqlalchemy import URL
from sqlalchemy.ext.asyncio import AsyncEngine

from config import bot, dp
from db.engine import create_engine, get_session_maker, proceed_schemas
from handlers import menu_handlers, user_handlers
from middlewares.middlewares import DBMiddleware


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

    postgres_url = URL.create(drivername='postgresql+asyncpg',
                              username=os.getenv('USER'),
                              password=os.getenv('PASSWORD'),
                              host=os.getenv('HOST'),
                              port=os.getenv('PORT'),
                              database='cookies_bot')

    async_engine: AsyncEngine = create_engine(postgres_url)

    # Creating DB connections pool
    pool = get_session_maker(async_engine)

    db_middleware = DBMiddleware(pool)
    # Добавляем мидлвари в диспетчер
    dp.update.middleware(db_middleware)

    # await proceed_schemas(async_engine, Base.metadata)

    await dp.start_polling(bot)
    await asyncio.Event().wait()


if __name__ == '__main__':
    asyncio.run(main())
