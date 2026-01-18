"""Contract tests for health check endpoint."""

import pytest
from datetime import datetime


@pytest.mark.contract
def test_health_endpoint_returns_200(client):
    """Test GET /health returns 200 status."""
    response = client.get("/health")

    assert response.status_code == 200


@pytest.mark.contract
def test_health_endpoint_returns_healthy_status(client):
    """Test GET /health returns status='healthy'."""
    response = client.get("/health")
    data = response.json()

    assert "status" in data
    assert data["status"] == "healthy"


@pytest.mark.contract
def test_health_endpoint_includes_timestamp(client):
    """Test GET /health includes timestamp field."""
    response = client.get("/health")
    data = response.json()

    assert "timestamp" in data
    # Verify timestamp is in ISO format
    timestamp_str = data["timestamp"]
    try:
        datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
        is_valid_timestamp = True
    except ValueError:
        is_valid_timestamp = False

    assert is_valid_timestamp, f"Timestamp '{timestamp_str}' is not in ISO format"


@pytest.mark.contract
def test_health_endpoint_response_time(client):
    """Test GET /health responds quickly (< 10ms target)."""
    import time

    start = time.time()
    response = client.get("/health")
    elapsed_ms = (time.time() - start) * 1000

    assert response.status_code == 200
    # Note: This is a soft check - actual p99 target is tested in integration
    assert elapsed_ms < 100, f"Health check took {elapsed_ms}ms, expected < 100ms"
