"""Prometheus metrics middleware."""

import time
import re
from prometheus_client import Counter, Histogram
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request


# Initialize Prometheus metrics
http_requests_total = Counter(
    "http_requests_total", "Total HTTP requests", ["method", "path", "status"]
)

http_request_duration_seconds = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency",
    ["method", "path"],
    buckets=(0.005, 0.01, 0.025, 0.05, 0.075, 0.1, 0.25, 0.5, 0.75, 1.0),
)


def normalize_path(path: str) -> str:
    """
    Normalize path to avoid high cardinality in metrics labels.
    Replace IDs with placeholders.
    """
    # Replace UUIDs and numeric IDs with {id}
    path = re.sub(r"/[0-9a-f-]+(?=/|$)", "/{id}", path)
    path = re.sub(r"/\d+(?=/|$)", "/{id}", path)
    return path


class MetricsMiddleware(BaseHTTPMiddleware):
    """Middleware to collect Prometheus metrics."""

    async def dispatch(self, request: Request, call_next):
        start_time = time.time()

        # Process request
        response = await call_next(request)

        # Calculate latency
        latency = time.time() - start_time

        # Normalize path to avoid high cardinality
        normalized_path = normalize_path(request.url.path)

        # Record metrics
        http_requests_total.labels(
            method=request.method, path=normalized_path, status=response.status_code
        ).inc()

        http_request_duration_seconds.labels(
            method=request.method, path=normalized_path
        ).observe(latency)

        return response
