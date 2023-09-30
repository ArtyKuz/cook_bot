from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import Message


class DBMiddleware(BaseMiddleware):
    def __init__(self, pool):
        super().__init__()
        self.pool = pool

    async def __call__(
            self,
            handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
            event: Message,
            data: Dict[str, Any]
    ) -> Any:
        async with self.pool() as session:
            data["session"] = session
            await handler(event, data)
