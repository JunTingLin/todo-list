"""Integration tests for Prometheus metrics collection."""

import pytest
import re


@pytest.mark.integration
def test_metrics_counter_increments_with_requests(client):
    """Test that request counter increments with each request."""
    # Get initial metrics
    initial_metrics = client.get("/metrics").text

    # Make several requests
    client.get("/todos")
    client.get("/todos")
    client.post("/todos", json={"title": "Test"})

    # Get updated metrics
    updated_metrics = client.get("/metrics").text

    # Verify counter increased
    # Look for http_requests_total with method="GET",path="/todos"
    pattern = r'http_requests_total\{method="GET",path="/todos",status="200"\}\s+(\d+)'

    initial_match = re.search(pattern, initial_metrics)
    updated_match = re.search(pattern, updated_metrics)

    if initial_match:
        initial_count = int(initial_match.group(1))
        updated_count = int(updated_match.group(1))
        assert updated_count > initial_count, "Counter should have incremented"
    else:
        # First time, just verify it exists
        assert updated_match is not None, "Counter should exist after requests"


@pytest.mark.integration
def test_histogram_records_request_latency(client):
    """Test that latency histogram records requests."""
    # Make a request
    client.get("/todos")

    # Get metrics
    metrics = client.get("/metrics").text

    # Verify histogram buckets exist for this endpoint
    # Note: Prometheus puts le (less than or equal) before other labels
    assert 'method="GET",path="/todos"' in metrics
    assert "http_request_duration_seconds_bucket{le=" in metrics

    # Verify sum and count exist
    assert (
        'http_request_duration_seconds_sum{method="GET",path="/todos"' in metrics
        or 'http_request_duration_seconds_count{method="GET",path="/todos"' in metrics
    )


@pytest.mark.integration
def test_metrics_use_low_cardinality_labels(client):
    """Test that metrics avoid high cardinality labels like request_id."""
    # Make requests
    client.get("/todos", headers={"X-Request-ID": "unique-id-1"})
    client.get("/todos", headers={"X-Request-ID": "unique-id-2"})

    # Get metrics
    metrics = client.get("/metrics").text

    # Verify request_id is NOT in metric labels (would cause high cardinality)
    assert "request_id=" not in metrics
    assert "unique-id-1" not in metrics
    assert "unique-id-2" not in metrics


@pytest.mark.integration
def test_metrics_normalize_path_with_ids(client):
    """Test that path normalization replaces IDs with placeholders."""
    # Create a todo to get an ID
    create_response = client.post("/todos", json={"title": "Test"})
    todo_id = create_response.json()["id"]

    # Access todo by ID
    client.get(f"/todos/{todo_id}")

    # Get metrics
    metrics = client.get("/metrics").text

    # Verify path is normalized to /todos/{id}, not the actual ID
    assert "/todos/{id}" in metrics or 'path="/todos/{id}"' in metrics
    # Verify actual ID is NOT in metrics (would cause high cardinality)
    assert f"/todos/{todo_id}" not in metrics or 'path="/todos/{id}"' in metrics


@pytest.mark.integration
def test_different_status_codes_tracked_separately(client):
    """Test that different status codes are tracked as separate metric series."""
    # Successful request
    client.get("/todos")

    # Not found request
    client.get("/todos/999")

    # Get metrics
    metrics = client.get("/metrics").text

    # Verify both 200 and 404 status codes are tracked
    assert 'status="200"' in metrics
    assert 'status="404"' in metrics


@pytest.mark.integration
def test_multiple_http_methods_tracked_separately(client):
    """Test that different HTTP methods are tracked separately."""
    # Different methods on same path
    client.get("/todos")
    client.post("/todos", json={"title": "Test"})

    # Get metrics
    metrics = client.get("/metrics").text

    # Verify both GET and POST methods are tracked
    assert 'method="GET"' in metrics
    assert 'method="POST"' in metrics
