"""Unit tests for Todo Pydantic models."""

import pytest
from pydantic import ValidationError
from src.models.todo import TodoCreate, TodoUpdate, TodoResponse


@pytest.mark.unit
def test_todo_create_with_valid_data():
    """Test TodoCreate with valid data."""
    todo = TodoCreate(title="Valid Todo", completed=False)

    assert todo.title == "Valid Todo"
    assert todo.completed is False


@pytest.mark.unit
def test_todo_create_default_completed_is_false():
    """Test TodoCreate defaults completed to False."""
    todo = TodoCreate(title="New Todo")

    assert todo.completed is False


@pytest.mark.unit
def test_todo_create_title_required():
    """Test TodoCreate requires title field."""
    with pytest.raises(ValidationError) as exc_info:
        TodoCreate()

    errors = exc_info.value.errors()
    assert any(error["loc"] == ("title",) for error in errors)


@pytest.mark.unit
def test_todo_create_empty_title_fails():
    """Test TodoCreate with empty string title fails validation."""
    with pytest.raises(ValidationError) as exc_info:
        TodoCreate(title="")

    errors = exc_info.value.errors()
    assert any(
        error["loc"] == ("title",) and "at least 1 character" in str(error)
        for error in errors
    )


@pytest.mark.unit
def test_todo_create_title_too_long_fails():
    """Test TodoCreate with title > 200 chars fails validation."""
    long_title = "a" * 201

    with pytest.raises(ValidationError) as exc_info:
        TodoCreate(title=long_title)

    errors = exc_info.value.errors()
    assert any(
        error["loc"] == ("title",) and "at most 200 characters" in str(error)
        for error in errors
    )


@pytest.mark.unit
def test_todo_create_title_exactly_200_chars():
    """Test TodoCreate with exactly 200 chars is valid."""
    title_200 = "a" * 200

    todo = TodoCreate(title=title_200)

    assert len(todo.title) == 200


@pytest.mark.unit
def test_todo_create_title_min_1_char():
    """Test TodoCreate with 1 char title is valid."""
    todo = TodoCreate(title="a")

    assert todo.title == "a"


@pytest.mark.unit
def test_todo_update_all_fields_optional():
    """Test TodoUpdate allows all fields to be optional."""
    update = TodoUpdate()

    assert update.title is None
    assert update.completed is None


@pytest.mark.unit
def test_todo_update_partial_title_only():
    """Test TodoUpdate with only title."""
    update = TodoUpdate(title="Updated Title")

    assert update.title == "Updated Title"
    assert update.completed is None


@pytest.mark.unit
def test_todo_update_partial_completed_only():
    """Test TodoUpdate with only completed status."""
    update = TodoUpdate(completed=True)

    assert update.title is None
    assert update.completed is True


@pytest.mark.unit
def test_todo_update_both_fields():
    """Test TodoUpdate with both fields."""
    update = TodoUpdate(title="New Title", completed=True)

    assert update.title == "New Title"
    assert update.completed is True


@pytest.mark.unit
def test_todo_update_empty_title_fails():
    """Test TodoUpdate with empty string fails validation."""
    with pytest.raises(ValidationError):
        TodoUpdate(title="")


@pytest.mark.unit
def test_todo_update_title_too_long_fails():
    """Test TodoUpdate with title > 200 chars fails validation."""
    long_title = "a" * 201

    with pytest.raises(ValidationError):
        TodoUpdate(title=long_title)


@pytest.mark.unit
def test_todo_response_with_all_fields():
    """Test TodoResponse with all required fields."""
    response = TodoResponse(id="123", title="Test Todo", completed=False)

    assert response.id == "123"
    assert response.title == "Test Todo"
    assert response.completed is False


@pytest.mark.unit
def test_todo_response_requires_all_fields():
    """Test TodoResponse requires all fields."""
    with pytest.raises(ValidationError) as exc_info:
        TodoResponse(id="123")

    errors = exc_info.value.errors()
    error_fields = [error["loc"][0] for error in errors]
    assert "title" in error_fields
    assert "completed" in error_fields


@pytest.mark.unit
def test_todo_response_from_dict():
    """Test TodoResponse can be created from dictionary."""
    data = {"id": "456", "title": "From Dict", "completed": True}

    response = TodoResponse(**data)

    assert response.id == "456"
    assert response.title == "From Dict"
    assert response.completed is True
