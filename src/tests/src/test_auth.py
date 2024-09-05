import jwt
import pytest
from fastapi import status

from core.config import JWT_ALGORITHM

from tests.fixtures.async_fixtures import client

endpoint = "/api/v1/auth"


def _signup_user(user_data):
    url = f"{endpoint}/signup"
    response = client.post(url=url, json=user_data).json()
    return response["access_token"], response["refresh_token"]


@pytest.mark.parametrize(
    "user_data, expected_status, expected_fields",
    [
        (
            {
                "login": "user1",
                "password": "pass1",
                "first_name": "user1_first_name",
                "last_name": "user1_last_name",
            },
            status.HTTP_200_OK,
            ("access_token", "refresh_token"),
        ),
        (
            {
                "password": "pass1",
                "first_name": "user1_first_name",
                "last_name": "user1_last_name",
            },
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            (),
        ),
        (
            {
                "login": "user1",
                "first_name": "user1_first_name",
                "last_name": "user1_last_name",
            },
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            (),
        ),
        (
            {
                "login": "",
                "password": "pass1",
                "first_name": "user1_first_name",
                "last_name": "user1_last_name",
            },
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            (),
        ),
        (
            {
                "login": "user1",
                "password": "",
                "first_name": "user1_first_name",
                "last_name": "user1_last_name",
            },
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            (),
        ),
        (
            {
                "login": "user1",
                "password": "pass1",
                "first_name": "",
                "last_name": "",
            },
            status.HTTP_200_OK,
            ("access_token", "refresh_token"),
        ),
        (
            {
                "login": "user1",
                "password": "pass1",
            },
            status.HTTP_200_OK,
            ("access_token", "refresh_token"),
        ),
    ],
)
@pytest.mark.asyncio
async def test_signup(user_data, expected_status, expected_fields):
    url = f"{endpoint}/signup"
    response = client.post(url=url, json=user_data)

    assert response.status_code == expected_status

    response_data = response.json()
    for field in expected_fields:
        assert field in response_data


@pytest.mark.asyncio
async def test_login_success():
    # Регистрируем пользователя и пытаемся залогиниться.
    login = "login_user1"
    password = "login_password1"

    access_token, refresh_token = _signup_user(
        {
            "login": login,
            "password": password,
            "first_name": "AAA",
            "last_name": "AAA",
        },
    )

    url = f"{endpoint}/login"
    login_response = client.post(
        url=url,
        json={
            "login": login,
            "password": password,
        },
    )

    assert login_response.status_code == status.HTTP_200_OK

    response_data = login_response.json()
    for field in ("access_token", "refresh_token"):
        assert field in response_data

    # Проверяем историю логинов пользователя
    payload = jwt.decode(
        access_token, options={"verify_signature": False}, algorithms=[JWT_ALGORITHM]
    )

    login_history_url = f"/api/v1/users/{payload['user_id']}/login_history"

    login_history_response = client.get(
        login_history_url,
        headers={
            "Authorization": f"Bearer {access_token}",
        },
    )

    assert login_history_response.status_code == status.HTTP_200_OK


@pytest.mark.parametrize(
    "user_data, expected_status, expected_fields",
    [
        (
            # Пользователь есть, но ввел неправильный пароль
            {
                "login": "admin_user",
                "password": "wrong_admin_password",
            },
            status.HTTP_400_BAD_REQUEST,
            (),
        ),
        (
            # Пользователя нет в БД
            {
                "login": "unknown_user",
                "password": "unknown_pass",
            },
            status.HTTP_404_NOT_FOUND,
            (),
        ),
        (
            # Введены некорректные данные
            {
                "password": "password",
            },
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            (),
        ),
        (
            # Введены некорректные данные
            {
                "login": "",
                "password": "password",
            },
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            (),
        ),
        (
            # Введены некорректные данные
            {
                "login": "unknown_user",
            },
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            (),
        ),
        (
            # Введены некорректные данные
            {
                "login": "unknown_user",
                "password": "",
            },
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            (),
        ),
    ],
)
@pytest.mark.asyncio
async def test_login_failed(create_admin, user_data, expected_status, expected_fields):
    url = f"{endpoint}/login"
    response = client.post(url=url, json=user_data)

    assert response.status_code == expected_status

    response_data = response.json()
    for field in expected_fields:
        assert field in response_data


@pytest.mark.asyncio
async def test_logout(
    create_moderator, access_token_moderator, refresh_token_moderator
):
    url = f"{endpoint}/logout"

    # Попытка разлогиниться с неправильными токенами
    wrong_access_token = access_token_moderator[::-1]
    wrong_refresh_token = refresh_token_moderator[::-1]
    response1 = client.post(
        url,
        json={"access_token": wrong_access_token, "refresh_token": wrong_refresh_token},
    )
    assert response1.status_code == status.HTTP_401_UNAUTHORIZED

    # Попытка разлогиниться с правильными токенами
    response2 = client.post(
        url,
        json={
            "access_token": access_token_moderator,
            "refresh_token": refresh_token_moderator,
        },
    )
    assert response2.status_code == status.HTTP_200_OK


@pytest.mark.asyncio
async def test_refresh(
    create_moderator, access_token_moderator, refresh_token_moderator
):
    refresh_url = f"{endpoint}/refresh"
    # Запрос на обновление с неправильными токенами
    wrong_access_token = access_token_moderator[::-1]
    wrong_refresh_token = refresh_token_moderator[::-1]
    response1 = client.post(
        refresh_url,
        json={"access_token": wrong_access_token, "refresh_token": wrong_refresh_token},
    )
    assert response1.status_code == status.HTTP_401_UNAUTHORIZED

    # Запрос на обновление с правильными токенами
    response2 = client.post(
        refresh_url,
        json={
            "access_token": access_token_moderator,
            "refresh_token": refresh_token_moderator,
        },
    )
    assert response2.status_code == status.HTTP_200_OK

    response2_data = response2.json()
    assert "access_token" in response2_data
    assert "refresh_token" in response2_data
