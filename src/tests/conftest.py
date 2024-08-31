import pytest
from fastapi.testclient import TestClient

from db.postgres import Base
from main import app


@pytest.fixture(scope="function")
def sqlalchemy_declarative_base():
    return Base


@pytest.fixture(scope="session")
def client():
    with TestClient(app) as client:
        yield client
