import pytest
import random
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_item(client: AsyncClient):
    """Test creating a new item."""
    # 使用随机用户ID
    test_user_id = random.randint(1000, 9999)
    
    item_data = {
        "name": "Test Item",
        "description": "A test item",
        "price": 99.99,
        "is_available": True
    }
    
    # 在请求头中设置用户ID
    headers = {"X-User-Id": str(test_user_id)}
    
    response = await client.post("/items/", json=item_data, headers=headers)
    assert response.status_code == 201
    
    data = response.json()
    assert data["name"] == item_data["name"]
    assert data["description"] == item_data["description"]
    assert data["price"] == item_data["price"]
    assert data["is_available"] == item_data["is_available"]
    assert "id" in data
    assert "user_id" in data
    assert data["user_id"] == test_user_id
    assert "created_at" in data
    assert "updated_at" in data


@pytest.mark.asyncio
async def test_get_item(client: AsyncClient):
    """Test getting an item by ID."""
    # 使用随机用户ID
    test_user_id = random.randint(1000, 9999)
    headers = {"X-User-Id": str(test_user_id)}
    
    # First create an item
    item_data = {
        "name": "Item to Get",
        "description": "This is an item to get by ID",
        "price": 39.99,
        "is_available": True
    }
    create_response = await client.post("/items/", json=item_data, headers=headers)
    assert create_response.status_code == 201
    item_id = create_response.json()["id"]
    
    # Now get the item
    get_response = await client.get(f"/items/{item_id}", headers=headers)
    assert get_response.status_code == 200
    
    data = get_response.json()
    assert data["id"] == item_id
    assert data["name"] == item_data["name"]
    assert data["description"] == item_data["description"]
    assert data["price"] == item_data["price"]
    assert data["user_id"] == test_user_id


@pytest.mark.asyncio
async def test_get_nonexistent_item(client: AsyncClient):
    """Test getting a non-existent item."""
    # 使用随机用户ID
    test_user_id = random.randint(1000, 9999)
    headers = {"X-User-Id": str(test_user_id)}
    
    response = await client.get("/items/999", headers=headers)
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_list_items(client: AsyncClient):
    """Test listing items with pagination."""
    # 使用随机用户ID
    test_user_id = random.randint(1000, 9999)
    headers = {"X-User-Id": str(test_user_id)}
    
    # Create a few items
    for i in range(5):
        item_data = {
            "name": f"Item {i+1}",
            "description": f"Description for item {i+1}",
            "price": (i+1) * 10.5,
            "is_available": i % 2 == 0
        }
        await client.post("/items/", json=item_data, headers=headers)
    
    # Get the list of items
    response = await client.get("/items/?page=1&page_size=3", headers=headers)
    assert response.status_code == 200
    
    data = response.json()
    assert data["total"] >= 5
    assert data["page"] == 1
    assert data["page_size"] == 3
    assert len(data["items"]) <= 3
    
    # Check that all items belong to our test user
    for item in data["items"]:
        assert item["user_id"] == test_user_id


@pytest.mark.asyncio
async def test_update_item(client: AsyncClient):
    """Test updating an item."""
    # 使用随机用户ID
    test_user_id = random.randint(1000, 9999)
    headers = {"X-User-Id": str(test_user_id)}
    
    # First create an item
    item_data = {
        "name": "Original Item",
        "description": "Original description",
        "price": 50.0,
        "is_available": True
    }
    create_response = await client.post("/items/", json=item_data, headers=headers)
    assert create_response.status_code == 201
    item_id = create_response.json()["id"]
    
    # Now update the item
    update_data = {
        "name": "Updated Item",
        "price": 75.0
    }
    update_response = await client.put(f"/items/{item_id}", json=update_data, headers=headers)
    assert update_response.status_code == 200
    
    data = update_response.json()
    assert data["id"] == item_id
    assert data["name"] == update_data["name"]
    assert data["price"] == update_data["price"]
    assert data["description"] == item_data["description"]  # Should remain unchanged
    assert data["user_id"] == test_user_id


@pytest.mark.asyncio
async def test_delete_item(client: AsyncClient):
    """Test deleting an item."""
    # 使用随机用户ID
    test_user_id = random.randint(1000, 9999)
    headers = {"X-User-Id": str(test_user_id)}
    
    # First create an item
    item_data = {
        "name": "Item to Delete",
        "description": "This item will be deleted",
        "price": 15.99,
        "is_available": True
    }
    create_response = await client.post("/items/", json=item_data, headers=headers)
    assert create_response.status_code == 201
    item_id = create_response.json()["id"]
    
    # Now delete the item
    delete_response = await client.delete(f"/items/{item_id}", headers=headers)
    assert delete_response.status_code == 204
    
    # Confirm it's deleted
    get_response = await client.get(f"/items/{item_id}", headers=headers)
    assert get_response.status_code == 404
