"""Contract tests for Todo API endpoints."""

import pytest


@pytest.mark.contract
def test_create_todo_returns_201_with_correct_schema(client):
    """Test POST /todos returns 201 status and correct response schema."""
    response = client.post("/todos", json={"title": "購買牛奶"})

    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["title"] == "購買牛奶"
    assert data["completed"] is False  # Default value


@pytest.mark.contract
def test_create_todo_with_completed_true(client):
    """Test POST /todos with completed=true."""
    response = client.post("/todos", json={"title": "已完成的任務", "completed": True})

    assert response.status_code == 201
    data = response.json()
    assert data["completed"] is True


@pytest.mark.contract
def test_create_todo_with_empty_title_returns_422(client):
    """Test POST /todos with empty title returns 422 validation error."""
    response = client.post("/todos", json={"title": ""})

    assert response.status_code == 422


@pytest.mark.contract
def test_create_todo_with_too_long_title_returns_422(client):
    """Test POST /todos with title > 200 chars returns 422 validation error."""
    long_title = "a" * 201
    response = client.post("/todos", json={"title": long_title})

    assert response.status_code == 422


@pytest.mark.contract
def test_get_todos_returns_200_with_array(client):
    """Test GET /todos returns 200 status and array response."""
    response = client.get("/todos")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.contract
def test_get_todos_returns_empty_array_when_no_todos(client):
    """Test GET /todos returns empty array when no todos exist."""
    response = client.get("/todos")

    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.contract
def test_get_todos_returns_all_todos(client):
    """Test GET /todos returns all created todos."""
    # Create 3 todos
    client.post("/todos", json={"title": "Task 1"})
    client.post("/todos", json={"title": "Task 2"})
    client.post("/todos", json={"title": "Task 3"})

    response = client.get("/todos")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3


@pytest.mark.contract
def test_get_todo_by_id_returns_200_with_todo(client):
    """Test GET /todos/{id} returns 200 status and single todo response."""
    # Create a todo first
    create_response = client.post("/todos", json={"title": "Test Todo"})
    todo_id = create_response.json()["id"]

    response = client.get(f"/todos/{todo_id}")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == todo_id
    assert data["title"] == "Test Todo"
    assert "completed" in data


@pytest.mark.contract
def test_get_todo_by_id_returns_404_when_not_found(client):
    """Test GET /todos/{id} returns 404 for non-existent todo."""
    response = client.get("/todos/999")

    assert response.status_code == 404


@pytest.mark.contract
def test_update_todo_returns_200_with_updated_data(client):
    """Test PUT /todos/{id} returns 200 status and updated response."""
    # Create a todo first
    create_response = client.post("/todos", json={"title": "Original Title"})
    todo_id = create_response.json()["id"]

    # Update the todo
    response = client.put(
        f"/todos/{todo_id}",
        json={"title": "Updated Title", "completed": True}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == todo_id
    assert data["title"] == "Updated Title"
    assert data["completed"] is True


@pytest.mark.contract
def test_update_todo_partial_update_title_only(client):
    """Test PUT /todos/{id} with only title update."""
    create_response = client.post("/todos", json={"title": "Original", "completed": False})
    todo_id = create_response.json()["id"]

    response = client.put(f"/todos/{todo_id}", json={"title": "New Title"})

    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "New Title"
    assert data["completed"] is False  # Should remain unchanged


@pytest.mark.contract
def test_update_todo_partial_update_completed_only(client):
    """Test PUT /todos/{id} with only completed status update."""
    create_response = client.post("/todos", json={"title": "Task"})
    todo_id = create_response.json()["id"]

    response = client.put(f"/todos/{todo_id}", json={"completed": True})

    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Task"  # Should remain unchanged
    assert data["completed"] is True


@pytest.mark.contract
def test_update_todo_returns_404_when_not_found(client):
    """Test PUT /todos/{id} returns 404 for non-existent todo."""
    response = client.put("/todos/999", json={"title": "Updated"})

    assert response.status_code == 404


@pytest.mark.contract
def test_delete_todo_returns_204(client):
    """Test DELETE /todos/{id} returns 204 status."""
    # Create a todo first
    create_response = client.post("/todos", json={"title": "To Delete"})
    todo_id = create_response.json()["id"]

    response = client.delete(f"/todos/{todo_id}")

    assert response.status_code == 204

    # Verify todo is deleted
    get_response = client.get(f"/todos/{todo_id}")
    assert get_response.status_code == 404


@pytest.mark.contract
def test_delete_todo_returns_404_when_not_found(client):
    """Test DELETE /todos/{id} returns 404 for non-existent todo."""
    response = client.delete("/todos/999")

    assert response.status_code == 404
