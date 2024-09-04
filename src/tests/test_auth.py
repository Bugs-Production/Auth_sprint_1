from time import sleep

import jwt
import pytest
from fastapi import status

from core.config import JWT_ALGORITHM
from tests.conftest import client

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
        # (
        #         {
        #             "password": "pass1",
        #             "first_name": "user1_first_name",
        #             "last_name": "user1_last_name",
        #         },
        #         status.HTTP_422_UNPROCESSABLE_ENTITY,
        #         (),
        # ),
        # (
        #         {
        #             "login": "user1",
        #             "first_name": "user1_first_name",
        #             "last_name": "user1_last_name",
        #         },
        #         status.HTTP_422_UNPROCESSABLE_ENTITY,
        #         (),
        # ),
        # (
        #         {
        #             "login": "",
        #             "password": "pass1",
        #             "first_name": "user1_first_name",
        #             "last_name": "user1_last_name",
        #         },
        #         status.HTTP_422_UNPROCESSABLE_ENTITY,
        #         (),
        # ),
        # (
        #         {
        #             "login": "user1",
        #             "password": "",
        #             "first_name": "user1_first_name",
        #             "last_name": "user1_last_name",
        #         },
        #         status.HTTP_422_UNPROCESSABLE_ENTITY,
        #         (),
        # ),
        # (
        #         {
        #             "login": "user1",
        #             "password": "pass1",
        #             "first_name": "",
        #             "last_name": "",
        #         },
        #         status.HTTP_200_OK,
        #         ("access_token", "refresh_token"),
        # ),
        # (
        #         {
        #             "login": "user1",
        #             "password": "pass1",
        #         },
        #         status.HTTP_200_OK,
        #         ("access_token", "refresh_token"),
        # ),
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
    sleep(5)

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


# @pytest.mark.parametrize(
#     "user_data, expected_status, expected_fields",
#     [
#         # (
#         #         {
#         #             "login": "login_user1",
#         #             "password": "wrong_admin_password",
#         #         },
#         #         status.HTTP_400_BAD_REQUEST,
#         #         (),
#         # ),
#         # (
#         #         {
#         #             "login": "unknown_user",
#         #             "password": "unknown_pass",
#         #
#         #         },
#         #         status.HTTP_404_NOT_FOUND,
#         #         (),
#         # ),
#         # (
#         #         {
#         #             "password": "password",
#         #         },
#         #         status.HTTP_422_UNPROCESSABLE_ENTITY,
#         #         (),
#         # ),
#         # (
#         #         {
#         #             "login": "",
#         #             "password": "password",
#         #
#         #         },
#         #         status.HTTP_422_UNPROCESSABLE_ENTITY,
#         #         (),
#         # ),
#         # (
#         #         {
#         #             "login": "unknown_user",
#         #         },
#         #         status.HTTP_422_UNPROCESSABLE_ENTITY,
#         #         (),
#         # ),
#         (
#             {
#                 "login": "unknown_user",
#                 "password": "",
#             },
#             status.HTTP_422_UNPROCESSABLE_ENTITY,
#             (),
#         ),
#     ],
# )
# @pytest.mark.asyncio
# async def test_login_failed(user_data, expected_status, expected_fields):
#     url = f"{endpoint}/login"
#     response = client.post(url=url, json=user_data)
#
#     assert response.status_code == expected_status
#
#     response_data = response.json()
#     for field in expected_fields:
#         assert field in response_data
#

@pytest.mark.asyncio
async def test_logout():
    access_token, refresh_token = _signup_user(
        {
            "login": "U1",
            "password": "pass1",
            "first_name": "U1",
            "last_name": "U1",
        },
    )
    url = f"{endpoint}/logout"

    wrong_access_token = access_token[::-1]
    wrong_refresh_token = refresh_token[::-1]
    response1 = client.post(
        url,
        json={"access_token": wrong_access_token, "refresh_token": wrong_refresh_token},
    )
    assert response1.status_code == status.HTTP_401_UNAUTHORIZED

    response2 = client.post(
        url, json={"access_token": access_token, "refresh_token": refresh_token}
    )
    assert response2.status_code == status.HTTP_200_OK
#
#
# @pytest.mark.asyncio
# async def test_refresh():
#     access_token, refresh_token = _signup_user(
#         {
#             "login": "U1",
#             "password": "pass1",
#             "first_name": "U1",
#             "last_name": "U1",
#         },
#     )
#
#     payload = jwt.decode(
#         access_token, options={"verify_signature": False}, algorithms=[JWT_ALGORITHM]
#     )
#
#     user_history_url = f"/api/v1/users/{payload['user_id']}/login_history"
#
#     login_response = client.get(
#         user_history_url,
#         headers={
#             "Authorization": f"Bearer {access_token}",
#         },
#     )
#     assert login_response.status_code == status.HTTP_200_OK
#
#     url = f"{endpoint}/refresh"
#
#     wrong_access_token = access_token[::-1]
#     wrong_refresh_token = refresh_token[::-1]
#     response1 = client.post(
#         url,
#         json={"access_token": wrong_access_token, "refresh_token": wrong_refresh_token},
#     )
#     assert response1.status_code == status.HTTP_401_UNAUTHORIZED
#
#     response2 = client.post(
#         url, json={"access_token": access_token, "refresh_token": refresh_token}
#     )
#     assert response2.status_code == status.HTTP_200_OK
#
#     response2_data = response2.json()
#     assert "access_token" in response2_data
#     assert "refresh_token" in response2_data
#
#     new_access_token = response2_data["access_token"]
#
#     login_response = client.get(
#         user_history_url,
#         headers={
#             "Authorization": f"Bearer {new_access_token}",
#         },
#     )
#     assert login_response.status_code == status.HTTP_200_OK
