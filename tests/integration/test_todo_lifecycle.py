"""Integration test for full todo lifecycle."""

import pytest


@pytest.mark.integration
def test_full_todo_lifecycle(client):
    """
    Test complete todo lifecycle: create → read → update → delete.
    This verifies the entire CRUD flow works end-to-end.
    """
    # 1. CREATE: Create a new todo
    create_response = client.post("/todos", json={
        "title": "學習 FastAPI",
        "completed": False
    })
    assert create_response.status_code == 201
    todo = create_response.json()
    todo_id = todo["id"]
    assert todo["title"] == "學習 FastAPI"
    assert todo["completed"] is False

    # 2. READ (single): Retrieve the created todo
    get_response = client.get(f"/todos/{todo_id}")
    assert get_response.status_code == 200
    retrieved_todo = get_response.json()
    assert retrieved_todo["id"] == todo_id
    assert retrieved_todo["title"] == "學習 FastAPI"

    # 3. READ (list): Verify todo appears in list
    list_response = client.get("/todos")
    assert list_response.status_code == 200
    todos_list = list_response.json()
    assert len(todos_list) == 1
    assert todos_list[0]["id"] == todo_id

    # 4. UPDATE: Update the todo's title and mark as completed
    update_response = client.put(f"/todos/{todo_id}", json={
        "title": "已完成學習 FastAPI",
        "completed": True
    })
    assert update_response.status_code == 200
    updated_todo = update_response.json()
    assert updated_todo["id"] == todo_id
    assert updated_todo["title"] == "已完成學習 FastAPI"
    assert updated_todo["completed"] is True

    # 5. READ (verify update): Verify changes persisted
    verify_response = client.get(f"/todos/{todo_id}")
    assert verify_response.status_code == 200
    verified_todo = verify_response.json()
    assert verified_todo["title"] == "已完成學習 FastAPI"
    assert verified_todo["completed"] is True

    # 6. DELETE: Delete the todo
    delete_response = client.delete(f"/todos/{todo_id}")
    assert delete_response.status_code == 204

    # 7. VERIFY DELETION: Confirm todo no longer exists
    get_deleted_response = client.get(f"/todos/{todo_id}")
    assert get_deleted_response.status_code == 404

    # 8. VERIFY LIST EMPTY: Confirm list is empty
    final_list_response = client.get("/todos")
    assert final_list_response.status_code == 200
    assert final_list_response.json() == []


@pytest.mark.integration
def test_multiple_todos_lifecycle(client):
    """Test managing multiple todos concurrently."""
    # Create multiple todos
    todos = []
    for i in range(3):
        response = client.post("/todos", json={"title": f"Task {i+1}"})
        assert response.status_code == 201
        todos.append(response.json())

    # Verify all todos exist
    list_response = client.get("/todos")
    assert len(list_response.json()) == 3

    # Update one todo
    client.put(f"/todos/{todos[1]['id']}", json={"completed": True})

    # Delete another todo
    client.delete(f"/todos/{todos[0]['id']}")

    # Verify final state
    final_list = client.get("/todos").json()
    assert len(final_list) == 2
    # Find the updated todo
    updated = [t for t in final_list if t["id"] == todos[1]["id"]][0]
    assert updated["completed"] is True
