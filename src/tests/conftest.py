import asyncio

import asyncpg
import pytest_asyncio
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import (AsyncSession, async_sessionmaker,
                                    create_async_engine)
from sqlalchemy.orm import declarative_base

from core.config import settings
from main import app

TestBase = declarative_base()
TEST_DATABASE_URL = settings.test_postgres_url
MAIN_DATABASE_URL = settings.postgres_url


async def create_database():
    # Создание подключения к основной базе данных
    conn = await asyncpg.connect(
        user=settings.postgres_user,
        password=settings.postgres_password,
        database=settings.postgres_db,
        host=settings.postgres_host,
        port=settings.postgres_port,
    )
    try:
        # Попытка создания базы данных, если она не существует
        await conn.execute(
            """
            CREATE DATABASE test_users_database
        """
        )
    except asyncpg.DuplicateDatabaseError:
        # База данных уже существует, ничего не делаем
        pass
    finally:
        await conn.close()


@pytest_asyncio.fixture(scope="session")
async def setup_test_db():
    # создание бд
    await create_database()

    engine = create_async_engine(TEST_DATABASE_URL, echo=True)
    async_session = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    # Асинхронное применение миграций
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", TEST_DATABASE_URL)
    await asyncio.to_thread(command.upgrade, alembic_cfg, "head")

    yield async_session

    # Очистка базы данных после завершения тестов
    async with engine.begin() as conn:
        await conn.run_sync(TestBase.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def db_session(setup_test_db):
    async_session = setup_test_db
    async with async_session() as session:
        yield session


@pytest_asyncio.fixture(scope="session")
def client():
    with TestClient(app) as client:
        yield client
