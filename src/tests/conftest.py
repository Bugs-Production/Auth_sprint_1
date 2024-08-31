import uuid
from datetime import datetime, timedelta

import jwt
import pytest
from fastapi.testclient import TestClient

from core import config
from core.config import settings
from db.postgres import Base
from main import app
from models.roles import Role
from models.user import User


@pytest.fixture(scope="function")
def sqlalchemy_declarative_base():
    return Base


@pytest.fixture(scope="session")
def client():
    with TestClient(app) as client:
        yield client


@pytest.fixture(scope="function")
def create_admin(mocked_session):
    # Создание роли админа
    admin_role = Role(id=uuid.uuid4(), title="admin")
    mocked_session.add(admin_role)
    mocked_session.commit()

    # Создание пользователя-админа
    admin_user = User(
        login="admin_user",
        password="admin_password",
        first_name="Admin",
        last_name="User",
    )
    admin_user.roles.append(admin_role)
    mocked_session.add(admin_user)
    mocked_session.commit()

    return admin_user


@pytest.fixture(scope="function")
def access_token_admin(create_admin):
    valid_till = datetime.now() + timedelta(hours=1)
    payload = {
        "user_id": str(create_admin.id),
        "exp": int(valid_till.timestamp()),
        "roles": [create_admin.roles[0].title],
    }

    token = jwt.encode(payload, settings.jwt_secret_key, algorithm=config.JWT_ALGORITHM)
    return token


@pytest.fixture(scope="function")
def access_token_moderator(create_admin):
    valid_till = datetime.now() + timedelta(hours=1)
    payload = {
        "user_id": str(create_admin.id),
        "exp": int(valid_till.timestamp()),
        "roles": ["moderator"],
    }

    token = jwt.encode(payload, settings.jwt_secret_key, algorithm=config.JWT_ALGORITHM)
    return token
