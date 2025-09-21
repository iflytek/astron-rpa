import pytest
import random
from httpx import AsyncClient

# 为 API Key 相关接口添加用户 ID 认证
USER_ID_HEADER = {"X-User-Id": "1234"}


@pytest.mark.asyncio
async def test_get_all_api_keys(client: AsyncClient):
    """Test getting all API keys."""
    response = await client.get("/api-keys", headers=USER_ID_HEADER)
    assert response.status_code == 200
    
    data = response.json()
    assert "data" in data
    assert isinstance(data["data"], list)
    
    # Check structure of API keys if any exist
    if data["data"]:
        api_key = data["data"][0]
        assert "id" in api_key
        assert "name" in api_key
        assert "created_at" in api_key


@pytest.mark.asyncio
async def test_create_api_key(client: AsyncClient):
    """Test creating a new API key."""
    # Generate a random suffix for the API key name
    random_suffix = random.randint(1000, 9999)
    
    api_key_data = {
        "name": f"Test API Key {random_suffix}"
    }
    
    response = await client.post("/api-keys", json=api_key_data, headers=USER_ID_HEADER)
    assert response.status_code == 201
    
    data = response.json()
    assert data["name"] == api_key_data["name"]
    assert "id" in data
    assert "key" in data
    assert "created_at" in data
    
    # Store the ID for the delete test
    return data["id"]


@pytest.mark.asyncio
async def test_delete_api_key(client: AsyncClient):
    """Test deleting an API key."""
    # First create an API key to ensure we have one to delete
    api_key_data = {
        "name": f"API Key to Delete {random.randint(1000, 9999)}"
    }
    
    create_response = await client.post("/api-keys", json=api_key_data, headers=USER_ID_HEADER)
    assert create_response.status_code == 201
    
    api_key_id = create_response.json()["id"]
    
    # Now delete the API key
    delete_response = await client.delete(f"/api-keys/{api_key_id}", headers=USER_ID_HEADER)
    assert delete_response.status_code == 204
    
    # Verify it's gone by getting all API keys and checking
    all_keys_response = await client.get("/api-keys", headers=USER_ID_HEADER)
    assert all_keys_response.status_code == 200
    
    all_keys = all_keys_response.json()["data"]
    assert not any(key["id"] == api_key_id for key in all_keys)


@pytest.mark.asyncio
async def test_delete_nonexistent_api_key(client: AsyncClient):
    """Test deleting a non-existent API key."""
    # Using a random ID that's unlikely to exist
    non_existent_id = f"non-existent-{random.randint(10000, 99999)}"
    response = await client.delete(f"/api-keys/{non_existent_id}", headers=USER_ID_HEADER)
    
    # It should return 404 (not found) or 204 (no content) if the API treats deletion of non-existent
    # resources as a successful operation (idempotent behavior)
    assert response.status_code in [404, 204]
    
    if response.status_code == 404:
        assert "不存在" in response.json()["detail"] or "not found" in response.json()["detail"].lower()
