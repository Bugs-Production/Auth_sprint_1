import pytest
from fastapi import status

from tests.conftest import client


class TestApiRoles:
    """Тестируем поведение endpoint /api/v1/roles/"""

    def setup_method(self):
        self.endpoint = "/api/v1/roles/"

    @pytest.mark.asyncio
    async def test_admin_can_successfully_get_roles(self, access_token_admin):
        response = client.get(
            self.endpoint, headers={"Authorization": f"Bearer {access_token_admin}"}
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json().get("items") == [
            {"id": "2e796639-9b3f-49c3-9c59-9c3302ae5e59", "title": "admin"}
        ]

    @pytest.mark.asyncio
    async def test_anonymous_user_request(self):
        response = client.get(self.endpoint)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json() == {"detail": "Not authenticated"}

    @pytest.mark.asyncio
    async def test_forbidden_access_with_non_admin_role(self, access_token_moderator):
        response = client.get(
            self.endpoint, headers={"Authorization": f"Bearer {access_token_moderator}"}
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.json() == {"detail": "Forbidden"}
