from typing import AsyncGenerator

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from src.core.config import settings


DATABASE_URL = settings.postgresql_url
ASYNC_DATABASE_URL = settings.async_postgresql_url

engine = create_engine(DATABASE_URL, echo=settings.ECHO)
async_engine = create_async_engine(ASYNC_DATABASE_URL, echo=settings.ECHO)

SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
)

AsyncSessionLocal = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


# Dependency
def get_db():
    """
    Независимый сеанс/соединение с базой данных (SessionLocal) для каждого запроса, использовать
    один и тот же сеанс для всех запросов, а затем закрыть его после завершения запроса.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_async_db() -> AsyncGenerator[AsyncSession, any]:
    """
    Асинхронный независимый сеанс/соединение с базой данных (SessionLocal).
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


class Base(DeclarativeBase):
    pass
