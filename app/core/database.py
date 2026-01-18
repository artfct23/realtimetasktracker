from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
    async_sessionmaker,
    AsyncEngine
)
from sqlalchemy.orm import declarative_base
from app.core.config import settings

Base = declarative_base()

class DatabaseHelper:
    def __init__(self, url: str, echo: bool = False):
        self.engine: AsyncEngine = create_async_engine(
            url=url,
            echo=echo,
            future=True,
            pool_pre_ping=True
        )
        self.session_factory: async_sessionmaker[AsyncSession] = async_sessionmaker(
            bind=self.engine,
            class_=AsyncSession,
            autoflush=False,
            autocommit=False,
            expire_on_commit=False,
        )

    async def dispose(self) -> None:
        await self.engine.dispose()

    async def session_getter(self) -> AsyncGenerator[AsyncSession, None]:
        async with self.session_factory() as session:
            try:
                yield session
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()

db_helper = DatabaseHelper(
    url=settings.DATABASE_URL,
    echo=True
)
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async for session in db_helper.session_getter():
        yield session

