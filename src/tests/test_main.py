import pytest


@pytest.mark.asyncio(loop_scope="function")
async def test_read_main(client, setup_test_db):
    response = client.get("/")
    assert response.status_code == 404
