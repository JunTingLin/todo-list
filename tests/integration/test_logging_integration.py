"""Integration tests for structured logging."""

import pytest
import json


@pytest.mark.integration
def test_structured_logging_format(client, capsys):
    """Test that logs are in JSON format with all required fields."""
    # Make a request
    client.get("/todos")

    # Capture stdout (where structlog outputs)
    captured = capsys.readouterr()

    # Parse the log line
    log_lines = [line for line in captured.out.split("\n") if line.strip()]
    assert len(log_lines) > 0, "No log output found"

    # Parse the JSON log
    log_entry = json.loads(log_lines[-1])

    # Verify required fields are present
    assert "request_id" in log_entry
    assert "timestamp" in log_entry
    assert "method" in log_entry
    assert "path" in log_entry
    assert "status_code" in log_entry
    assert "latency_ms" in log_entry
    assert "event" in log_entry

    # Verify values
    assert log_entry["method"] == "GET"
    assert log_entry["path"] == "/todos"
    assert log_entry["status_code"] == 200
    assert isinstance(log_entry["latency_ms"], (int, float))
    assert log_entry["latency_ms"] >= 0


@pytest.mark.integration
def test_request_id_appears_in_logs_and_response(client, capsys):
    """Test that request_id appears in both logs and response headers."""
    custom_id = "test-request-id-123"

    # Make request with custom request_id
    response = client.get("/todos", headers={"X-Request-ID": custom_id})

    # Verify response header contains the request_id
    assert response.headers["X-Request-ID"] == custom_id

    # Capture and verify log contains the same request_id
    captured = capsys.readouterr()
    log_lines = [line for line in captured.out.split("\n") if line.strip()]
    log_entry = json.loads(log_lines[-1])

    assert log_entry["request_id"] == custom_id


@pytest.mark.integration
def test_logging_captures_different_http_methods(client, capsys):
    """Test that logs capture different HTTP methods correctly."""
    # Make different types of requests
    client.get("/todos")
    captured_get = capsys.readouterr()

    client.post("/todos", json={"title": "Test"})
    captured_post = capsys.readouterr()

    # Parse logs
    get_log = json.loads(
        [line for line in captured_get.out.split("\n") if line.strip()][-1]
    )
    post_log = json.loads(
        [line for line in captured_post.out.split("\n") if line.strip()][-1]
    )

    assert get_log["method"] == "GET"
    assert post_log["method"] == "POST"


@pytest.mark.integration
def test_logging_captures_different_status_codes(client, capsys):
    """Test that logs capture different status codes correctly."""
    # Successful request
    client.get("/todos")
    captured_success = capsys.readouterr()

    # Not found request
    client.get("/todos/999")
    captured_not_found = capsys.readouterr()

    # Parse logs
    success_log = json.loads(
        [line for line in captured_success.out.split("\n") if line.strip()][-1]
    )
    not_found_log = json.loads(
        [line for line in captured_not_found.out.split("\n") if line.strip()][-1]
    )

    assert success_log["status_code"] == 200
    assert not_found_log["status_code"] == 404


@pytest.mark.integration
def test_logging_includes_timestamp_in_iso_format(client, capsys):
    """Test that logs include timestamp in ISO 8601 format."""
    client.get("/todos")
    captured = capsys.readouterr()

    log_lines = [line for line in captured.out.split("\n") if line.strip()]
    log_entry = json.loads(log_lines[-1])

    # Verify timestamp exists and ends with 'Z' (ISO format)
    timestamp = log_entry["timestamp"]
    assert timestamp.endswith("Z")
    assert "T" in timestamp  # ISO format includes 'T' separator


@pytest.mark.integration
def test_no_sensitive_information_in_logs(client, capsys):
    """Test that logs don't contain sensitive information."""
    # Make a request with potentially sensitive data in title
    client.post("/todos", json={"title": "秘密任務: password123"})
    captured = capsys.readouterr()

    # Verify the sensitive title content is NOT in logs
    # (Only request metadata should be logged, not request body)
    assert "password123" not in captured.out
    assert "秘密任務" not in captured.out
