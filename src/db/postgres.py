from typing import Optional

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base

from core.config import settings

Base = declarative_base()

engine: Optional[create_async_engine] = None
async_session: Optional[async_sessionmaker] = None

dsn = settings.postgres_url
