from typing import Callable, Dict, Any, Awaitable

import asyncpg
from aiogram import types, BaseMiddleware
from aiogram.types import Message


class DBMiddleware(BaseMiddleware):
    def __init__(self, pool: asyncpg.pool.Pool):
        super().__init__()
        self.pool = pool

    async def __call__(
            self,
            handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
            event: Message,
            data: Dict[str, Any]
    ) -> Any:
        async with self.pool.acquire() as conn:
            data["conn"] = conn
            await handler(event, data)

    # async def release(self, conn):
    #     print('запуск метода release')
    #     await self.pool.release(conn)
    # async def on_pre_process_message(self, message: types.Message, data: dict):
    #     # Получаем подключение из пула
    #     conn = await self.pool.acquire()
    #     # Сохраняем его в контексте сообщения
    #     data['conn'] = conn
    #
    # async def on_post_process_message(self, message: types.Message, result, data: dict):
    #     # Закрываем подключение
    #     await self.pool.release(data['conn'])
    #     # Удаляем его из контекста сообщения
    #     del data['conn']
    #
    # async def on_pre_process_callback_query(self, callback_query: types.CallbackQuery, data: dict):
    #     # Получаем подключение из пула
    #     conn = await self.pool.acquire()
    #     # Сохраняем его в контексте сообщения
    #     data['conn'] = conn
    #
    # async def on_post_process_callback_query(self, callback_query: types.CallbackQuery, result, data: dict):
    #     # Закрываем подключение
    #     await self.pool.release(data['conn'])
    #     # Удаляем его из контекста сообщения
    #     del data['conn']