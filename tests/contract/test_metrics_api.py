"""Contract tests for metrics endpoint."""

import pytest


@pytest.mark.contract
def test_metrics_endpoint_returns_200(client):
    """Test GET /metrics returns 200 status."""
    response = client.get("/metrics")

    assert response.status_code == 200


@pytest.mark.contract
def test_metrics_endpoint_returns_text_plain(client):
    """Test GET /metrics returns text/plain content type."""
    response = client.get("/metrics")

    assert "text/plain" in response.headers["content-type"]


@pytest.mark.contract
def test_metrics_endpoint_returns_prometheus_format(client):
    """Test GET /metrics returns data in Prometheus format."""
    response = client.get("/metrics")
    content = response.text

    # Prometheus format should contain:
    # - HELP lines
    # - TYPE lines
    # - Metric lines with labels

    assert "# HELP" in content
    assert "# TYPE" in content

    # Should contain our defined metrics
    assert "http_requests_total" in content
    assert "http_request_duration_seconds" in content


@pytest.mark.contract
def test_metrics_include_request_counter(client):
    """Test that metrics include http_requests_total counter."""
    # Make a request to generate metrics
    client.get("/todos")

    response = client.get("/metrics")
    content = response.text

    assert "http_requests_total" in content
    # Should have method, path, and status labels
    assert "method=" in content
    assert "path=" in content
    assert "status=" in content


@pytest.mark.contract
def test_metrics_include_latency_histogram(client):
    """Test that metrics include http_request_duration_seconds histogram."""
    # Make a request to generate metrics
    client.get("/todos")

    response = client.get("/metrics")
    content = response.text

    assert "http_request_duration_seconds" in content
    # Histogram should have buckets
    assert "_bucket{" in content
    assert "_sum{" in content or "_sum " in content
    assert "_count{" in content or "_count " in content
