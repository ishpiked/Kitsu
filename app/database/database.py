from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.pool import NullPool
from app.config.settings import settings


class Base(DeclarativeBase):
    pass


def _create_engine():
    return create_async_engine(
        settings.DATABASE_URL,
        echo=settings.is_development,
        poolclass=NullPool,
    )


def _create_session_maker():
    return async_sessionmaker(
        _create_engine(),
        class_=AsyncSession,
        expire_on_commit=False,
    )


async def get_session() -> AsyncSession:
    session_maker = _create_session_maker()
    async with session_maker() as session:
        yield session


async def init_db() -> None:
    engine = _create_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await engine.dispose()


async def close_db() -> None:
    pass