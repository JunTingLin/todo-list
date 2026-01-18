"""In-memory storage for todo items."""

import threading
from typing import Dict, List, Optional
from src.models.todo import TodoCreate, TodoUpdate, TodoResponse


class TodoStore:
    """Thread-safe in-memory storage for todo items."""

    def __init__(self):
        self._todos: Dict[str, Dict[str, any]] = {}
        self._lock = threading.Lock()
        self._counter = 0

    def create(self, todo: TodoCreate) -> TodoResponse:
        """Create a new todo item with thread-safe ID generation."""
        with self._lock:
            self._counter += 1
            todo_id = str(self._counter)
            todo_dict = {
                "id": todo_id,
                "title": todo.title,
                "completed": todo.completed,
            }
            self._todos[todo_id] = todo_dict
            return TodoResponse(**todo_dict)

    def get(self, todo_id: str) -> Optional[TodoResponse]:
        """Retrieve a todo item by ID with thread safety."""
        with self._lock:
            todo_dict = self._todos.get(todo_id)
            if todo_dict:
                return TodoResponse(**todo_dict)
            return None

    def list_all(self) -> List[TodoResponse]:
        """Return all todo items with thread safety."""
        with self._lock:
            return [TodoResponse(**todo_dict) for todo_dict in self._todos.values()]

    def update(self, todo_id: str, todo_update: TodoUpdate) -> Optional[TodoResponse]:
        """Update an existing todo item with thread safety."""
        with self._lock:
            if todo_id not in self._todos:
                return None

            # Update fields if provided
            if todo_update.title is not None:
                self._todos[todo_id]["title"] = todo_update.title
            if todo_update.completed is not None:
                self._todos[todo_id]["completed"] = todo_update.completed

            return TodoResponse(**self._todos[todo_id])

    def delete(self, todo_id: str) -> bool:
        """Remove a todo item with thread safety. Returns True if deleted, False if not found."""
        with self._lock:
            if todo_id in self._todos:
                del self._todos[todo_id]
                return True
            return False

    def clear(self):
        """Clear all todos (for testing purposes)."""
        with self._lock:
            self._todos.clear()
            self._counter = 0


# Global instance
_store = TodoStore()


def get_todo_store() -> TodoStore:
    """Get the global todo store instance."""
    return _store
