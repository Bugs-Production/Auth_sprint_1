from fastapi import status


class TestApiRoles:
    """Тестируем поведение endpoint /api/v1/roles/"""

    def setup_method(self):
        self.endpoint = "/api/v1/roles/"

    def test_admin_can_successfully_get_roles(self, client, access_token_admin):
        response = client.get(
            self.endpoint, headers={"Authorization": f"Bearer {access_token_admin}"}
        )
        assert response.status_code == status.HTTP_200_OK

    def test_anonymous_user_request(self, client):
        response = client.get(self.endpoint)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json() == {"detail": "Not authenticated"}

    def test_forbidden_access_with_non_admin_role(self, client, access_token_moderator):
        response = client.get(
            self.endpoint, headers={"Authorization": f"Bearer {access_token_moderator}"}
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.json() == {"detail": "Forbidden"}
