import pytest
import random
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_all_workflows(client: AsyncClient, api_key):
    """Test getting all workflows."""
    headers = {"Authorization": f"Bearer {api_key['key']}"}
    response = await client.get("/workflows", headers=headers)
    assert response.status_code == 200

    data = response.json()
    assert "data" in data
    assert isinstance(data["data"], list)


@pytest.mark.asyncio
async def test_get_workflow(client: AsyncClient, api_key):
    """Test getting a specific workflow by project_id."""
    headers = {"Authorization": f"Bearer {api_key['key']}"}
    
    # First, get all workflows to pick one
    list_response = await client.get("/workflows", headers=headers)
    assert list_response.status_code == 200

    all_workflows = list_response.json()["data"]
    if not all_workflows:
        pytest.skip("No workflows available for testing")

    # Get a specific workflow
    project_id = all_workflows[0]["project_id"]
    get_response = await client.get(f"/workflows/{project_id}", headers=headers)
    assert get_response.status_code == 200

    workflow = get_response.json()
    assert workflow["project_id"] == project_id
    assert "name" in workflow
    assert "status" in workflow


@pytest.mark.asyncio
async def test_get_nonexistent_workflow(client: AsyncClient, api_key):
    """Test getting a non-existent workflow."""
    headers = {"Authorization": f"Bearer {api_key['key']}"}
    
    # Using a random ID that's unlikely to exist
    non_existent_id = f"non-existent-{random.randint(10000, 99999)}"
    response = await client.get(f"/workflows/{non_existent_id}", headers=headers)
    assert response.status_code == 404
    assert "不存在" in response.json()["detail"] or "not found" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_execute_workflow_sync(client: AsyncClient, api_key):
    """Test synchronous execution of a workflow."""
    headers = {"Authorization": f"Bearer {api_key['key']}"}
    
    # First, get all workflows to pick one
    list_response = await client.get("/workflows", headers=headers)
    assert list_response.status_code == 200

    all_workflows = list_response.json()["data"]
    if not all_workflows:
        pytest.skip("No workflows available for testing")

    # Find an active workflow
    active_workflow = next((w for w in all_workflows if w["status"] == 1), None)
    if not active_workflow:
        pytest.skip("No active workflows available for testing")

    # Execute the workflow synchronously
    project_id = active_workflow["project_id"]
    execution_data = {
        "parameters": {
            "test_param": "test_value"
        }
    }

    response = await client.post(f"/workflows/{project_id}/execute", json=execution_data, headers=headers)
    # Note: This might return 202 if the execution takes too long
    assert response.status_code in [200, 202]


@pytest.mark.asyncio
async def test_execute_workflow_async(client: AsyncClient, api_key):
    """Test asynchronous execution of a workflow."""
    headers = {"Authorization": f"Bearer {api_key['key']}"}
    
    # First, get all workflows to pick one
    list_response = await client.get("/workflows", headers=headers)
    assert list_response.status_code == 200

    all_workflows = list_response.json()["data"]
    if not all_workflows:
        pytest.skip("No workflows available for testing")

    # Find an active workflow
    active_workflow = next((w for w in all_workflows if w["status"] == 1), None)
    if not active_workflow:
        pytest.skip("No active workflows available for testing")

    # Execute the workflow asynchronously
    project_id = active_workflow["project_id"]
    execution_data = {
        "parameters": {
            "test_param": "test_value"
        }
    }

    response = await client.post(f"/workflows/{project_id}/execute-async", json=execution_data, headers=headers)
    assert response.status_code == 202

    data = response.json()
    assert "executionId" in data
    assert isinstance(data["executionId"], str)


@pytest.mark.asyncio
async def test_get_execution_status(client: AsyncClient, api_key):
    """Test getting execution status."""
    headers = {"Authorization": f"Bearer {api_key['key']}"}
    
    # First, execute a workflow asynchronously to get an execution ID
    list_response = await client.get("/workflows", headers=headers)
    assert list_response.status_code == 200

    all_workflows = list_response.json()["data"]
    if not all_workflows:
        pytest.skip("No workflows available for testing")

    # Find an active workflow
    active_workflow = next((w for w in all_workflows if w["status"] == 1), None)
    if not active_workflow:
        pytest.skip("No active workflows available for testing")

    # Execute the workflow asynchronously
    project_id = active_workflow["project_id"]
    execution_data = {
        "parameters": {
            "test_param": "test_value"
        }
    }

    execute_response = await client.post(f"/workflows/{project_id}/execute-async", json=execution_data, headers=headers)
    assert execute_response.status_code == 202

    execution_id = execute_response.json()["executionId"]

    # Get the execution status
    status_response = await client.get(f"/executions/{execution_id}", headers=headers)
    assert status_response.status_code == 200

    data = status_response.json()
    assert data["id"] == execution_id
    assert data["project_id"] == project_id
    assert "status" in data
    assert data["status"] in ["PENDING", "RUNNING", "COMPLETED", "FAILED", "CANCELLED"]


@pytest.mark.asyncio
async def test_get_nonexistent_execution(client: AsyncClient, api_key):
    """Test getting a non-existent execution."""
    headers = {"Authorization": f"Bearer {api_key['key']}"}
    
    # Using a random ID that's unlikely to exist
    non_existent_id = f"non-existent-{random.randint(10000, 99999)}"
    response = await client.get(f"/executions/{non_existent_id}", headers=headers)
    assert response.status_code == 404
    assert "不存在" in response.json()["detail"] or "not found" in response.json()["detail"].lower()
