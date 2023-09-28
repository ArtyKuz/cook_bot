from typing import Any, Awaitable, Callable, Dict

import asyncpg
from aiogram import BaseMiddleware, types
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
