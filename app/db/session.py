import os
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from app.core.config import settings  

# Асинхронный движок для PostgreSQL
DATABASE_URL = settings.DATABASE_URL  

engine = create_async_engine(
    DATABASE_URL,
    echo=True,  # лог SQL-запросов, можно отключить в prod
    future=True,
)

# Асинхронный sessionmaker
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    class_=AsyncSession,
)


# Контекстный менеджер для использования с async with
@asynccontextmanager
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


from sqlalchemy.exc import OperationalError
import asyncio

async def wait_for_db(engine, retries=15):
    for i in range(retries):
        try:
            async with engine.begin() as conn:
                await conn.execute(text("SELECT 1"))
            return
        except (OperationalError, OSError):
            await asyncio.sleep(2)
    raise RuntimeError("Database is not available")
