"""Pytest configuration and fixtures."""

import pytest
from fastapi.testclient import TestClient
from src.main import app
from src.storage.memory import get_todo_store


@pytest.fixture
def client():
    """FastAPI TestClient fixture."""
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_storage():
    """Reset todo storage before each test."""
    store = get_todo_store()
    store.clear()
    yield
    store.clear()


@pytest.fixture
def todo_store():
    """Get todo store instance."""
    return get_todo_store()
