"""Contract tests for X-Request-ID header handling."""

import pytest
import uuid


@pytest.mark.contract
def test_response_includes_request_id_header(client):
    """Test that response includes X-Request-ID header."""
    response = client.get("/")

    assert "X-Request-ID" in response.headers
    assert response.headers["X-Request-ID"] is not None


@pytest.mark.contract
def test_custom_request_id_is_returned(client):
    """Test that custom X-Request-ID sent in request is returned in response."""
    custom_id = "custom-request-id-12345"

    response = client.get("/", headers={"X-Request-ID": custom_id})

    assert response.headers["X-Request-ID"] == custom_id


@pytest.mark.contract
def test_auto_generated_request_id_is_uuid_format(client):
    """Test that auto-generated request_id follows UUID format."""
    response = client.get("/")

    request_id = response.headers["X-Request-ID"]
    # Verify it's a valid UUID
    try:
        uuid.UUID(request_id)
        is_valid_uuid = True
    except ValueError:
        is_valid_uuid = False

    assert is_valid_uuid, f"Request ID '{request_id}' is not a valid UUID"


@pytest.mark.contract
def test_different_requests_get_different_request_ids(client):
    """Test that different requests without custom request_id get unique IDs."""
    response1 = client.get("/")
    response2 = client.get("/")

    request_id1 = response1.headers["X-Request-ID"]
    request_id2 = response2.headers["X-Request-ID"]

    assert request_id1 != request_id2


@pytest.mark.contract
def test_request_id_present_in_all_endpoints(client):
    """Test that X-Request-ID header is present across all endpoints."""
    # Test root endpoint
    response = client.get("/")
    assert "X-Request-ID" in response.headers

    # Test todos endpoints
    response = client.get("/todos")
    assert "X-Request-ID" in response.headers

    response = client.post("/todos", json={"title": "Test"})
    assert "X-Request-ID" in response.headers
