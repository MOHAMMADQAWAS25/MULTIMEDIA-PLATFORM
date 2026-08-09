from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from src.infrastructure.config import settings


class Base(DeclarativeBase):
    pass


def get_engine_connect_args(database_url: str) -> dict[str, int]:
    if database_url.startswith("postgresql+asyncpg://"):
        return {"statement_cache_size": 0}
    return {}


engine = create_async_engine(
    settings.database_url,
    connect_args=get_engine_connect_args(settings.database_url),
    pool_pre_ping=True,
)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)


async def get_db_session() -> AsyncIterator[AsyncSession]:
    async with AsyncSessionLocal() as session:
        yield session
