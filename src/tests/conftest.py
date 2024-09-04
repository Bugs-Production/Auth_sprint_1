import asyncio
import uuid
from datetime import datetime, timedelta
from typing import AsyncGenerator

import asyncpg
import jwt
import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import (AsyncSession, async_sessionmaker,
                                    create_async_engine)
from sqlalchemy.pool import NullPool

from db.postgres import Base, get_postgres_session
from main import app
from models.roles import Role
from models.user import User
from tests.core.config import JWT_ALGORITHM, settings

# DATABASE
DATABASE_URL_TEST = settings.postgres_url

engine_test = create_async_engine(DATABASE_URL_TEST, poolclass=NullPool, echo=True)
async_session_maker = async_sessionmaker(
    bind=engine_test, class_=AsyncSession, expire_on_commit=False
)
metadata = Base.metadata
metadata.bind = engine_test


async def override_get_async_session() -> AsyncGenerator[AsyncSession, None]:
    return async_session_maker


app.dependency_overrides[get_postgres_session] = override_get_async_session


@pytest.fixture(autouse=True, scope="session")
async def prepare_database():
    async with engine_test.begin() as conn:
        await conn.run_sync(metadata.create_all)
    yield
    async with engine_test.begin() as conn:
        await conn.run_sync(metadata.drop_all)


# SETUP
@pytest.fixture(scope="session")
def event_loop(request):
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


client = TestClient(app)


@pytest.fixture(scope="session")
async def ac() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


# Fixtures for tests
@pytest.fixture(scope="function")
async def create_admin():
    # Создание роли админа
    async with async_session_maker() as session:
        admin_role = Role(id="2e796639-9b3f-49c3-9c59-9c3302ae5e59", title="admin")
        session.add(admin_role)
        await session.commit()

        # Создание пользователя-админа
        admin_user = User(
            login="admin_user",
            password="admin_password",
            first_name="Admin",
            last_name="User",
        )
        admin_user.roles.append(admin_role)
        session.add(admin_user)
        await session.commit()

        return admin_user


@pytest.fixture(scope="function")
async def access_token_admin(create_admin):
    valid_till = datetime.now() + timedelta(hours=1)
    payload = {
        "user_id": str(create_admin.id),
        "exp": int(valid_till.timestamp()),
        "roles": ["admin"],
    }

    token = jwt.encode(payload, settings.jwt_secret_key, algorithm=JWT_ALGORITHM)
    return token


@pytest.fixture(scope="function")
async def create_moderator():
    # Создание роли модератора
    async with async_session_maker() as session:
        moderator_role = Role(id=uuid.uuid4(), title="moderator")
        session.add(moderator_role)
        await session.commit()

        # Создание пользователя-модератора
        moderator = User(
            login="moderator_user",
            password="moderator_password",
            first_name="Moderator",
            last_name="Bla",
        )
        moderator.roles.append(moderator_role)
        session.add(moderator)
        await session.commit()

        return moderator


@pytest.fixture(scope="function")
async def access_token_moderator(create_moderator):
    valid_till = datetime.now() + timedelta(hours=1)
    payload = {
        "user_id": str(create_moderator.id),
        "exp": int(valid_till.timestamp()),
        "roles": ["moderator"],
    }

    token = jwt.encode(payload, settings.jwt_secret_key, algorithm=JWT_ALGORITHM)
    return token
