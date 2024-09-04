import pytest
from fastapi import status

from tests.conftest import client

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
