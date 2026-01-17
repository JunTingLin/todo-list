"""Request ID middleware for tracking requests."""

import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Middleware to generate or extract request IDs for tracking."""

    async def dispatch(self, request: Request, call_next):
        # Extract request_id from header or generate new one
        request_id = request.headers.get("X-Request-ID")
        if not request_id:
            request_id = str(uuid.uuid4())

        # Store in request state for access in handlers
        request.state.request_id = request_id

        # Process request
        response = await call_next(request)

        # Add request_id to response headers
        response.headers["X-Request-ID"] = request_id

        return response
