from aiogram import Bot, Dispatcher
import asyncio
from services.services import get_recipe, get_list_of_dishes
from aiogram.fsm.storage.memory import MemoryStorage
from handlers import menu_handlers, user_handlers

token = '5817292849:AAE1RtekgcdqwtlDRU3Inbyb96oywPcIWi4'

bot = Bot(token=token, parse_mode='HTML')
storage: MemoryStorage = MemoryStorage()

dp: Dispatcher = Dispatcher(storage=storage)

dp.include_router(menu_handlers.router)
dp.include_router(user_handlers.router)


# async def main():
#     await get_list_of_dishes()
#     await get_recipe()


if __name__ == '__main__':
    dp.run_polling(bot)
    # asyncio.run(main())
