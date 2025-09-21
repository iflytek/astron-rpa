import pytest
from httpx import AsyncClient
import time


@pytest.mark.asyncio
async def test_execution_workflow_and_status(client: AsyncClient, api_key):
    """Test the full flow: execute a workflow and check its status."""
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
            "test_param_1": "test_value_1",
            "test_param_2": 42
        }
    }
    
    execute_response = await client.post(f"/workflows/{project_id}/execute-async", json=execution_data, headers=headers)
    assert execute_response.status_code == 202
    
    execution_id = execute_response.json()["executionId"]
    
    # Check status a few times with delay to see if it completes
    max_attempts = 5
    completed = False
    
    for _ in range(max_attempts):
        status_response = await client.get(f"/executions/{execution_id}", headers=headers)
        assert status_response.status_code == 200
        
        execution = status_response.json()
        assert execution["id"] == execution_id
        
        # If execution completed or failed, we can break
        if execution["status"] in ["COMPLETED", "FAILED"]:
            completed = True
            break
        
        # Wait a bit before checking again
        time.sleep(1)
    
    # Even if it didn't complete in our test window, we've verified we can retrieve status
    # Check that all expected fields are present
    execution = status_response.json()
    assert "project_id" in execution
    assert "start_time" in execution
    assert "status" in execution
    
    # If it completed, check for result or error
    if completed and execution["status"] == "COMPLETED":
        assert "result" in execution
        assert "end_time" in execution
    elif completed and execution["status"] == "FAILED":
        assert "error" in execution
        assert "end_time" in execution


@pytest.mark.asyncio
async def test_execution_status_enum_values(client: AsyncClient, api_key):
    """Test that the execution status follows the defined enum values."""
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
    
    execute_response = await client.post(f"/workflows/{project_id}/execute-async", json=execution_data, headers=headers)
    assert execute_response.status_code == 202
    
    execution_id = execute_response.json()["executionId"]
    
    # Check the status
    status_response = await client.get(f"/executions/{execution_id}", headers=headers)
    assert status_response.status_code == 200
    
    # Verify the status is one of the expected enum values
    valid_statuses = ["PENDING", "RUNNING", "COMPLETED", "FAILED", "CANCELLED"]
    assert status_response.json()["status"] in valid_statuses


@pytest.mark.asyncio
async def test_execution_with_different_parameters(client: AsyncClient, api_key):
    """Test workflow execution with different parameter types."""
    headers = {"Authorization": f"Bearer {api_key['key']}"}
    
    # First, get an active workflow
    list_response = await client.get("/workflows", headers=headers)
    assert list_response.status_code == 200
    
    all_workflows = list_response.json()["data"]
    if not all_workflows:
        pytest.skip("No workflows available for testing")
    
    project_id = all_workflows[0]["project_id"]
    
    # Test with various parameter types
    test_cases = [
        {"string_param": "test value"},
        {"number_param": 42},
        {"boolean_param": True},
        {"array_param": [1, 2, 3]},
        {"object_param": {"key": "value"}},
        {"mixed_params": {"string": "value", "number": 42, "boolean": True}}
    ]
    
    for params in test_cases:
        execution_data = {"parameters": params}
        
        response = await client.post(f"/workflows/{project_id}/execute-async", json=execution_data, headers=headers)
        assert response.status_code == 202
        
        execution_id = response.json()["executionId"]
        assert execution_id is not None
        
        # Verify the parameters were stored with the execution
        status_response = await client.get(f"/executions/{execution_id}", headers=headers)
        assert status_response.status_code == 200
        
        # Check that parameters match what we sent
        # Note: Some APIs may not return the full parameters in the status response
        if "parameters" in status_response.json():
            stored_params = status_response.json()["parameters"]
            for key, value in params.items():
                assert key in stored_params
                assert stored_params[key] == value 