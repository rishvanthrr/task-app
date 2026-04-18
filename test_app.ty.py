import pytest
from app import app  # Import your Flask app

@pytest.fixture
def client():
    """Fixture to provide a test client for the Flask app."""
    app.config['TESTING'] = True  # Enable testing mode
    with app.test_client() as client:
        yield client

def test_home(client):
    """Test the home route."""
    response = client.get('/')
    assert response.status_code == 200
    assert b"Task Manager API Running!" in response.data

def test_get_tasks_empty(client):
    """Test GET /tasks when no tasks exist."""
    response = client.get('/tasks')
    assert response.status_code == 200
    assert response.get_json() == []

def test_add_task(client):
    """Test POST /tasks to add a task."""
    task_data = {"title": "Test Task", "description": "A test task"}
    response = client.post('/tasks', json=task_data)
    assert response.status_code == 200
    data = response.get_json()
    assert data["message"] == "Task added"
    assert len(data["tasks"]) == 1
    assert data["tasks"][0] == task_data

def test_get_tasks_after_add(client):
    """Test GET /tasks after adding a task."""
    # First, add a task (using the same client session)
    task_data = {"title": "Another Task"}
    client.post('/tasks', json=task_data)
    
    response = client.get('/tasks')
    assert response.status_code == 200
    tasks = response.get_json()
    assert len(tasks) == 1  # Assuming this runs after the previous test; in reality, use fixtures for isolation
    assert tasks[0]["title"] == "Another Task"

def test_delete_task_valid(client):
    """Test DELETE /tasks/<index> for a valid index."""
    # Add a task first
    task_data = {"title": "Task to Delete"}
    client.post('/tasks', json=task_data)
    
    # Delete it
    response = client.delete('/tasks/0')
    assert response.status_code == 200
    assert response.get_json()["message"] == "Task deleted"
    
    # Verify it's gone
    response = client.get('/tasks')
    assert response.get_json() == []

def test_delete_task_invalid(client):
    """Test DELETE /tasks/<index> for an invalid index."""
    response = client.delete('/tasks/99')  # Index out of range
    assert response.status_code == 200
    assert response.get_json()["message"] == "Task not found"