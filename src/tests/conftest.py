import asyncio
import uuid
from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import (AsyncEngine, AsyncSession,
                                    create_async_engine)
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from core.config import settings
from db.postgres import Base
from main import app
from models.roles import Role
from models.user import User

TEST_DATABASE_URL = settings.postgres_url

# Service and model fixtures


@pytest_asyncio.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
def client():
    with TestClient(app) as client:
        yield client


@pytest.fixture(scope="session")
def test_engine() -> AsyncEngine:
    engine = create_async_engine(
        TEST_DATABASE_URL, echo=settings.sql_echo, poolclass=NullPool
    )
    yield engine


@pytest_asyncio.fixture(scope="function")
async def test_session(test_engine: AsyncEngine) -> AsyncGenerator[AsyncSession, None]:
    async_session = sessionmaker(
        test_engine, class_=AsyncSession, expire_on_commit=False
    )
    async with test_engine.connect() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
        await conn.commit()

        async with async_session() as session:
            yield session

        await conn.run_sync(Base.metadata.drop_all)


# Tests data


# Example
@pytest_asyncio.fixture(scope="function")
async def create_admin(test_session):
    # Создание роли админа
    admin_role = Role(id=uuid.uuid4(), title="admin")
    test_session.add(admin_role)
    await test_session.commit()

    # Создание пользователя-админа
    admin_user = User(
        login="admin_user",
        password="admin_password",
        first_name="Admin",
        last_name="User",
    )
    admin_user.roles.append(admin_role)
    test_session.add(admin_user)
    await test_session.commit()

    return admin_user
