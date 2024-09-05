import pytest
from fastapi import status

from tests import constants

endpoint = "/api/v1/auth"


@pytest.mark.asyncio
async def test_login_success(async_client, moderator, access_token_moderator):
    url = f"{endpoint}/login"
    login_response = await async_client.post(
        url=url,
        json={
            "login": constants.MODERATOR_LOGIN,
            "password": constants.MODERATOR_PASSWORD,
        },
    )

    assert login_response.status_code == status.HTTP_200_OK

    response_data = login_response.json()
    for field in ("access_token", "refresh_token"):
        assert field in response_data

    # Проверяем историю логинов пользователя

    login_history_url = f"/api/v1/users/{moderator.id}/login_history"

    login_history_response = await async_client.get(
        login_history_url,
        headers={
            "Authorization": f"Bearer {access_token_moderator}",
        },
    )

    assert login_history_response.status_code == status.HTTP_200_OK
