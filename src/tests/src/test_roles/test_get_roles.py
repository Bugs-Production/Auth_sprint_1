import pytest
from fastapi import status


class TestApiGetRoles:
    """Тестируем поведение endpoint GET /api/v1/roles/"""

    def setup_method(self):
        self.endpoint = "/api/v1/roles/"

    # Фикстура для заголовков авторизации администратора
    @pytest.fixture
    def headers_admin(self, access_token_admin):
        return {"Authorization": f"Bearer {access_token_admin}"}

    # Фикстура для заголовков авторизации модератора
    @pytest.fixture
    def headers_moderator(self, access_token_moderator):
        return {"Authorization": f"Bearer {access_token_moderator}"}

    @pytest.mark.asyncio
    async def test_admin_can_successfully_get_roles(self, async_client, headers_admin):
        response = await async_client.get(self.endpoint, headers=headers_admin)
        assert response.status_code == status.HTTP_200_OK, "Admin should have access"
        assert response.json().get("items") == [
            {"id": "2e796639-9b3f-49c3-9c59-9c3302ae5e59", "title": "admin"}
        ], "Role data mismatch"

    @pytest.mark.asyncio
    async def test_anonymous_user_request(self, async_client):
        response = await async_client.get(self.endpoint)
        assert (
            response.status_code == status.HTTP_401_UNAUTHORIZED
        ), "Anonymous users should not have access"
        assert response.json() == {
            "detail": "Not authenticated"
        }, "Error message mismatch for unauthenticated request"

    @pytest.mark.asyncio
    async def test_forbidden_access_with_non_admin_role(
        self, async_client, headers_moderator
    ):
        response = await async_client.get(self.endpoint, headers=headers_moderator)
        assert (
            response.status_code == status.HTTP_403_FORBIDDEN
        ), "Non-admin should not have access"
        assert response.json() == {
            "detail": "Forbidden"
        }, "Error message mismatch for unauthorized access"
