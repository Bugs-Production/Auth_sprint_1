import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import (AsyncSession, async_sessionmaker,
                                    create_async_engine)
from sqlalchemy.orm import declarative_base

from core.config import settings
from main import app

TestBase = declarative_base()
DATABASE_URL = settings.test_postgres_url


@pytest.fixture(scope="session")
async def setup_test_db():
    # Настройка движка и сессии
    engine = create_async_engine(DATABASE_URL, echo=True)
    async_session = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    # Применение миграций
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", DATABASE_URL)
    command.upgrade(alembic_cfg, "head")

    yield async_session

    # Очистка базы данных после завершения тестов
    async with engine.begin() as conn:
        await conn.run_sync(TestBase.metadata.drop_all)

    await engine.dispose()


@pytest.fixture(scope="function")
async def db_session(setup_test_db):
    async with setup_test_db() as session:
        yield session


@pytest.fixture(scope="session")
def client():
    with TestClient(app) as client:
        yield client
