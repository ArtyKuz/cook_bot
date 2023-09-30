from sqlalchemy import URL
from sqlalchemy.ext.asyncio import (AsyncEngine, AsyncSession,
                                    async_sessionmaker, create_async_engine)


def create_engine(url: str | URL) -> AsyncEngine:
    return create_async_engine(url)


async def proceed_schemas(engine: AsyncEngine, metadata) -> None:
    async with engine.begin() as conn:
        await conn.run_sync(metadata.create_all)


def get_session_maker(engine: AsyncEngine) -> async_sessionmaker:
    return async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
