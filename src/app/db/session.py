from __future__ import annotations

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.app.settings import settings


class Database:
    def __init__(self, database_url: str, *, echo: bool = False):
        self.engine = create_async_engine(
            database_url,
            echo=echo,
            future=True,
        )
        self.SessionLocal = async_sessionmaker(
            bind=self.engine,
            expire_on_commit=False,
            autoflush=False,
            class_=AsyncSession,
        )

    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        async with self.SessionLocal() as session:
            yield session

    async def dispose(self) -> None:
        await self.engine.dispose()
