"""Unit tests for TodoStore."""

import pytest
from src.models.todo import TodoCreate, TodoUpdate
from src.storage.memory import TodoStore


@pytest.fixture
def store():
    """Create a fresh TodoStore for each test."""
    store = TodoStore()
    yield store
    store.clear()


@pytest.mark.unit
def test_create_todo(store):
    """Test creating a new todo item."""
    todo = TodoCreate(title="Test Todo", completed=False)

    result = store.create(todo)

    assert result.id is not None
    assert result.title == "Test Todo"
    assert result.completed is False


@pytest.mark.unit
def test_create_multiple_todos_have_unique_ids(store):
    """Test that multiple todos get unique IDs."""
    todo1 = store.create(TodoCreate(title="Todo 1"))
    todo2 = store.create(TodoCreate(title="Todo 2"))
    todo3 = store.create(TodoCreate(title="Todo 3"))

    assert todo1.id != todo2.id
    assert todo2.id != todo3.id
    assert todo1.id != todo3.id


@pytest.mark.unit
def test_get_existing_todo(store):
    """Test retrieving an existing todo by ID."""
    created = store.create(TodoCreate(title="Existing Todo"))

    result = store.get(created.id)

    assert result is not None
    assert result.id == created.id
    assert result.title == "Existing Todo"


@pytest.mark.unit
def test_get_non_existent_todo_returns_none(store):
    """Test retrieving non-existent todo returns None."""
    result = store.get("999")

    assert result is None


@pytest.mark.unit
def test_list_all_empty_store(store):
    """Test listing all todos when store is empty."""
    result = store.list_all()

    assert result == []


@pytest.mark.unit
def test_list_all_with_multiple_todos(store):
    """Test listing all todos returns all created todos."""
    store.create(TodoCreate(title="Todo 1"))
    store.create(TodoCreate(title="Todo 2"))
    store.create(TodoCreate(title="Todo 3"))

    result = store.list_all()

    assert len(result) == 3
    titles = [todo.title for todo in result]
    assert "Todo 1" in titles
    assert "Todo 2" in titles
    assert "Todo 3" in titles


@pytest.mark.unit
def test_update_todo_title(store):
    """Test updating todo title."""
    created = store.create(TodoCreate(title="Original Title"))

    updated = store.update(created.id, TodoUpdate(title="New Title"))

    assert updated is not None
    assert updated.id == created.id
    assert updated.title == "New Title"
    assert updated.completed == created.completed  # Should remain unchanged


@pytest.mark.unit
def test_update_todo_completed(store):
    """Test updating todo completed status."""
    created = store.create(TodoCreate(title="Task", completed=False))

    updated = store.update(created.id, TodoUpdate(completed=True))

    assert updated is not None
    assert updated.completed is True
    assert updated.title == created.title  # Should remain unchanged


@pytest.mark.unit
def test_update_todo_both_fields(store):
    """Test updating both title and completed status."""
    created = store.create(TodoCreate(title="Old", completed=False))

    updated = store.update(
        created.id,
        TodoUpdate(title="New", completed=True)
    )

    assert updated is not None
    assert updated.title == "New"
    assert updated.completed is True


@pytest.mark.unit
def test_update_non_existent_todo_returns_none(store):
    """Test updating non-existent todo returns None."""
    result = store.update("999", TodoUpdate(title="Updated"))

    assert result is None


@pytest.mark.unit
def test_delete_existing_todo(store):
    """Test deleting an existing todo."""
    created = store.create(TodoCreate(title="To Delete"))

    result = store.delete(created.id)

    assert result is True
    # Verify it's actually deleted
    assert store.get(created.id) is None


@pytest.mark.unit
def test_delete_non_existent_todo_returns_false(store):
    """Test deleting non-existent todo returns False."""
    result = store.delete("999")

    assert result is False


@pytest.mark.unit
def test_clear_store(store):
    """Test clearing all todos from store."""
    store.create(TodoCreate(title="Todo 1"))
    store.create(TodoCreate(title="Todo 2"))

    store.clear()

    assert store.list_all() == []
    # Verify counter is also reset
    new_todo = store.create(TodoCreate(title="First After Clear"))
    assert new_todo.id == "1"


@pytest.mark.unit
def test_thread_safety_sequential_ids(store):
    """Test that IDs are generated sequentially even with multiple operations."""
    todo1 = store.create(TodoCreate(title="First"))
    todo2 = store.create(TodoCreate(title="Second"))
    todo3 = store.create(TodoCreate(title="Third"))

    # IDs should be sequential
    assert int(todo2.id) == int(todo1.id) + 1
    assert int(todo3.id) == int(todo2.id) + 1
