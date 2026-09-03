import os
from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.ext.declarative import declarative_base

POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_DB = os.getenv("POSTGRES_DB")

if not POSTGRES_USER or not POSTGRES_PASSWORD or not POSTGRES_DB:
    exit("Ошибка. Не найдено ключей")

DATABASE_URL = (
    f"postgresql+asyncpg://{POSTGRES_USER}"
    f":{POSTGRES_PASSWORD}@postgres:5432/{POSTGRES_DB}"
)

engine = create_async_engine(DATABASE_URL, echo=True)
Base = declarative_base()
SessionLocal = async_sessionmaker(engine, expire_on_commit=False)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        yield session
