from typing import AsyncGenerator, Optional

from sqlalchemy.ext.asyncio import (AsyncSession, async_sessionmaker,
                                    create_async_engine)
from sqlalchemy.orm import declarative_base

from core.config import settings

Base = declarative_base()

engine: Optional[create_async_engine] = None
async_session: Optional[async_sessionmaker] = None

dsn = settings.postgres_url


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session
