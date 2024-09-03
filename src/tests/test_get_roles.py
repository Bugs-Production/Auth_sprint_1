import pytest
from fastapi import status

# from tests.conftest import client, test_session, access_token_admin, access_token_moderator

class TestApiRoles:
    """Тестируем поведение endpoint /api/v1/roles/"""

    def setup_method(self):
        self.endpoint = "/api/v1/roles/"

    @pytest.mark.asyncio
    async def test_admin_can_successfully_get_roles(
        self, client, access_token_admin, test_session
    ):
        response = client.get(
            self.endpoint, headers={"Authorization": f"Bearer {access_token_admin}"}
        )
        assert response.status_code == status.HTTP_200_OK

    @pytest.mark.asyncio
    async def test_anonymous_user_request(self, client, test_session):
        response = client.get(self.endpoint)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json() == {"detail": "Not authenticated"}

    @pytest.mark.asyncio
    async def test_forbidden_access_with_non_admin_role(
        self, client, test_session, access_token_moderator
    ):
        response = client.get(
            self.endpoint, headers={"Authorization": f"Bearer {access_token_moderator}"}
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.json() == {"detail": "Forbidden"}
