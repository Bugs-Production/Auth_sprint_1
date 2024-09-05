import pytest
from fastapi import status


class TestAuthLogout:
    def setup_method(self):
        self.endpoint = "/api/v1/auth/refresh"

    @pytest.mark.asyncio
    async def test_refresh(
        self, async_client, moderator, access_token_moderator, refresh_token_moderator
    ):
        # Запрос на обновление с неправильными токенами
        wrong_access_token = access_token_moderator[::-1]
        wrong_refresh_token = refresh_token_moderator[::-1]
        response1 = await async_client.post(
            self.endpoint,
            json={
                "access_token": wrong_access_token,
                "refresh_token": wrong_refresh_token,
            },
        )
        assert response1.status_code == status.HTTP_401_UNAUTHORIZED

        # Запрос на обновление с правильными токенами
        response2 = await async_client.post(
            self.endpoint,
            json={
                "access_token": access_token_moderator,
                "refresh_token": refresh_token_moderator,
            },
        )
        assert response2.status_code == status.HTTP_200_OK

        response2_data = response2.json()
        assert "access_token" in response2_data
        assert "refresh_token" in response2_data