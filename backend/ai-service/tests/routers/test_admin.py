from httpx import AsyncClient
import pytest

@pytest.mark.asyncio
async def test_get_user_list(client: AsyncClient):
    params = {
        "user_id": "abcd",
    }
    response = await client.get("/admin/user/points", params=params)
    assert response.status_code == 200
    assert "user_point" in response.json()
    assert isinstance(response.json()["user_point"], int)
    assert response.json()["user_point"] == 0

@pytest.mark.asyncio
async def test_add_user_points(client: AsyncClient):
    params = {
        "user_id": "abcd",
        "amount": 100,
    }
    response = await client.post("/admin/user/points", params=params)
    assert response.status_code == 200
    assert response.json()["user_point"]["remaining_amount"] == 100

    params = {
        "user_id": "abcd",
    }
    response = await client.get("/admin/user/points", params=params)
    assert response.status_code == 200
    assert response.json()["user_point"] == 100 # Error: assert 200 == 100
