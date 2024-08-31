from fastapi import status


def test_get_roles(client):
    response = client.get("http://localhost:8000/api/v1/roles/")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
