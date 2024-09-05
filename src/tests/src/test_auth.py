import pytest
from fastapi import status

endpoint = "/api/v1/auth"


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
async def test_signup(async_client, user_data, expected_status, expected_fields):
    url = f"{endpoint}/signup"
    response = await async_client.post(url=url, json=user_data)

    assert response.status_code == expected_status

    response_data = response.json()
    for field in expected_fields:
        assert field in response_data


@pytest.mark.asyncio
async def test_login_success(async_client, create_moderator, access_token_moderator):
    url = f"{endpoint}/login"
    login_response = await async_client.post(
        url=url,
        json={
            "login": "moderator_user",
            "password": "moderator_password",
        },
    )

    assert login_response.status_code == status.HTTP_200_OK

    response_data = login_response.json()
    for field in ("access_token", "refresh_token"):
        assert field in response_data

    # Проверяем историю логинов пользователя

    login_history_url = f"/api/v1/users/{create_moderator.id}/login_history"

    login_history_response = await async_client.get(
        login_history_url,
        headers={
            "Authorization": f"Bearer {access_token_moderator}",
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
async def test_login_failed(
    async_client, create_admin, user_data, expected_status, expected_fields
):
    url = f"{endpoint}/login"
    response = await async_client.post(url=url, json=user_data)

    assert response.status_code == expected_status

    response_data = response.json()
    for field in expected_fields:
        assert field in response_data


@pytest.mark.asyncio
async def test_logout(
    async_client, create_moderator, access_token_moderator, refresh_token_moderator
):
    url = f"{endpoint}/logout"

    # Попытка разлогиниться с неправильными токенами
    wrong_access_token = access_token_moderator[::-1]
    wrong_refresh_token = refresh_token_moderator[::-1]
    response1 = await async_client.post(
        url,
        json={"access_token": wrong_access_token, "refresh_token": wrong_refresh_token},
    )
    assert response1.status_code == status.HTTP_401_UNAUTHORIZED

    # Попытка разлогиниться с правильными токенами
    response2 = await async_client.post(
        url,
        json={
            "access_token": access_token_moderator,
            "refresh_token": refresh_token_moderator,
        },
    )
    assert response2.status_code == status.HTTP_200_OK


@pytest.mark.asyncio
async def test_refresh(
    async_client, create_moderator, access_token_moderator, refresh_token_moderator
):
    refresh_url = f"{endpoint}/refresh"
    # Запрос на обновление с неправильными токенами
    wrong_access_token = access_token_moderator[::-1]
    wrong_refresh_token = refresh_token_moderator[::-1]
    response1 = await async_client.post(
        refresh_url,
        json={"access_token": wrong_access_token, "refresh_token": wrong_refresh_token},
    )
    assert response1.status_code == status.HTTP_401_UNAUTHORIZED

    # Запрос на обновление с правильными токенами
    response2 = await async_client.post(
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
