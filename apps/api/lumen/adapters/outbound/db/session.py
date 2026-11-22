"""PostgreSQL session lifecycle."""

from contextlib import asynccontextmanager
from collections.abc import Callable

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

class DatabaseSessions:
    def __init__(self, database_url: Callable[[], str]):
        self._database_url = database_url

    @asynccontextmanager
    async def scope(self):
        engine = create_async_engine(self._database_url())
        factory = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
        try:
            async with factory() as session:
                try:
                    yield session
                except Exception:
                    await session.rollback()
                    raise
        finally:
            await engine.dispose()
