from time import sleep

import pytest
from fastapi import status
from sqlalchemy.sql import select

from models import RefreshToken
from tests import constants
from tests.fixtures.db_fixtures import async_session_maker


class TestAuthLogout:
    def setup_method(self):
        self.endpoint = "/api/v1/auth/logout"

    @pytest.mark.asyncio
    async def test_logout(
        self, async_client, moderator, access_token_moderator, refresh_token_moderator
    ):

        # Попытка разлогиниться с неправильными токенами
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

        # Попытка разлогиниться с правильными токенами
        response2 = await async_client.post(
            self.endpoint,
            json={
                "access_token": access_token_moderator,
                "refresh_token": refresh_token_moderator,
            },
        )
        assert response2.status_code == status.HTTP_200_OK

    @pytest.mark.asyncio
    async def test_logout_all(
        self, async_client, moderator, access_token_moderator, refresh_token_moderator
    ):
        logout_all_url = f"{self.endpoint}/all"
        login_url = "/api/v1/auth/login"

        # Создаем несколько подключений пользователя, имитируя, подключения с разных устройств
        for i in range(2):
            sleep(1)  # для того чтобы создались разные access, refresh токены
            await async_client.post(
                login_url,
                json={
                    "login": constants.MODERATOR_LOGIN,
                    "password": constants.MODERATOR_PASSWORD,
                },
            )

        # Делаем logout для всех подключений, кроме текущего
        logout_response = await async_client.post(
            logout_all_url,
            json={
                "refresh_token": refresh_token_moderator,
                "access_token": access_token_moderator,
            },
        )
        assert logout_response.status_code == status.HTTP_200_OK
        assert logout_response.json() == constants.LOGOUT_ALL_JSON

        # Проверяем, что у пользователя остался единственный токен
        async with async_session_maker() as session:
            result1 = await session.scalars(
                select(RefreshToken).where(RefreshToken.user_id == moderator.id)
            )

            user_refresh_tokens = result1.all()

        assert len(user_refresh_tokens) == 1
        assert user_refresh_tokens[0].token == refresh_token_moderator
