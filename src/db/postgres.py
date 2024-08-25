from typing import Optional

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    AsyncEngine,
)
from sqlalchemy.orm import declarative_base

from core.config import settings

Base = declarative_base()

engine: Optional[AsyncEngine] = None
async_session: Optional[AsyncSession] = None

dsn = settings.postgres_url


async def get_postgres() -> AsyncSession:
    return async_session
