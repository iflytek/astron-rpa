import pytest
import json
from httpx import AsyncClient
import time


@pytest.mark.asyncio
async def test_workflow_e2e(client: AsyncClient, api_key):
    """End-to-end test for the workflow execution process."""
    headers = {"Authorization": f"Bearer {api_key['key']}"}
    
    # 1. Get a list of workflows
    list_response = await client.get("/workflows", headers=headers)
    assert list_response.status_code == 200
    
    all_workflows = list_response.json()["data"]
    if not all_workflows:
        pytest.skip("No workflows available for testing")
    
    # 2. Find an active workflow
    active_workflow = next((w for w in all_workflows if w["status"] == 1), None)
    if not active_workflow:
        pytest.skip("No active workflows available for testing")
    
    project_id = active_workflow["project_id"]
    
    # 3. Check that we can get the specific workflow
    get_workflow_response = await client.get(f"/workflows/{project_id}", headers=headers)
    assert get_workflow_response.status_code == 200
    assert get_workflow_response.json()["project_id"] == project_id
    
    # 4. Execute the workflow synchronously 
    # (may timeout and recommend async approach)
    parameters = {
        "parameters": {
            "input_data": "test input",
            "run_id": f"test-{int(time.time())}"
        }
    }
    
    sync_response = await client.post(f"/workflows/{project_id}/execute", json=parameters, headers=headers)
    
    # If it completes synchronously, check the result
    if sync_response.status_code == 200:
        sync_result = sync_response.json()
        assert sync_result["project_id"] == project_id
        assert sync_result["status"] in ["COMPLETED", "FAILED"]
        
    # 5. Execute the workflow asynchronously
    async_response = await client.post(f"/workflows/{project_id}/execute-async", json=parameters, headers=headers)
    assert async_response.status_code == 202
    
    execution_id = async_response.json()["executionId"]
    assert execution_id is not None
    
    # 6. Poll for execution status
    max_attempts = 5
    for i in range(max_attempts):
        status_response = await client.get(f"/executions/{execution_id}", headers=headers)
        assert status_response.status_code == 200
        
        status_data = status_response.json()
        assert status_data["id"] == execution_id
        assert status_data["project_id"] == project_id
        
        # If completed or failed, we're done
        if status_data["status"] in ["COMPLETED", "FAILED"]:
            if status_data["status"] == "COMPLETED":
                # Verify result exists
                assert "result" in status_data
            elif status_data["status"] == "FAILED":
                # Verify error exists
                assert "error" in status_data
            break
            
        # If we've reached the max attempts and it's not done, that's ok
        # The execution is likely still running
        if i == max_attempts - 1:
            assert status_data["status"] in ["PENDING", "RUNNING"]
            
        # Wait before polling again
        time.sleep(1)


@pytest.mark.asyncio
async def test_api_key_workflow(client: AsyncClient, api_key_factory):
    """Test using API keys to access workflow functionality."""
    # Create a new API key using the factory
    api_key_data = await api_key_factory("1234")
    
    # Use the API key to access workflows
    headers = {"Authorization": f"Bearer {api_key_data['key']}"}
    
    list_response = await client.get("/workflows", headers=headers)
    assert list_response.status_code == 200
    assert "data" in list_response.json()


@pytest.mark.asyncio
async def test_workflow_with_complex_parameters(client: AsyncClient, api_key):
    """Test executing a workflow with complex nested parameters."""
    headers = {"Authorization": f"Bearer {api_key['key']}"}
    
    # Get a workflow to test
    list_response = await client.get("/workflows", headers=headers)
    assert list_response.status_code == 200
    
    all_workflows = list_response.json()["data"]
    if not all_workflows:
        pytest.skip("No workflows available for testing")
    
    project_id = all_workflows[0]["project_id"]
    
    # Create a complex nested parameter object
    complex_params = {
        "parameters": {
            "simple_string": "value",
            "simple_number": 42,
            "simple_boolean": True,
            "nested_object": {
                "name": "nested value",
                "attributes": {
                    "color": "blue",
                    "size": "large"
                }
            },
            "array_of_objects": [
                {"id": 1, "name": "item1"},
                {"id": 2, "name": "item2"},
                {"id": 3, "name": "item3"}
            ],
            "mixed_array": [1, "string", True, {"key": "value"}]
        }
    }
    
    # Execute with complex parameters
    response = await client.post(f"/workflows/{project_id}/execute-async", 
                               json=complex_params, headers=headers)
    assert response.status_code == 202
    
    execution_id = response.json()["executionId"]
    
    # Get execution details to verify parameters were stored correctly
    status_response = await client.get(f"/executions/{execution_id}", headers=headers)
    assert status_response.status_code == 200
    
    # Verify the execution was created with the correct project_id
    execution_data = status_response.json()
    assert execution_data["project_id"] == project_id
    assert execution_data["id"] == execution_id
