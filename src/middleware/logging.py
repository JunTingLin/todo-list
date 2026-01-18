"""Structured logging middleware."""

import time
import structlog
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

# Configure structlog
structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer(),
    ],
    logger_factory=structlog.PrintLoggerFactory(),
)

logger = structlog.get_logger()


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to log all HTTP requests with structured logging."""

    async def dispatch(self, request: Request, call_next):
        # Get request_id from request state (set by RequestIDMiddleware)
        request_id = getattr(request.state, "request_id", "unknown")

        # Bind request_id to logging context
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(request_id=request_id)

        start_time = time.time()

        try:
            # Process request
            response = await call_next(request)

            # Calculate latency
            latency_ms = (time.time() - start_time) * 1000

            # Log successful request
            logger.info(
                "request_completed",
                method=request.method,
                path=request.url.path,
                status_code=response.status_code,
                latency_ms=round(latency_ms, 2),
            )

            return response

        except Exception as exc:
            # Calculate latency
            latency_ms = (time.time() - start_time) * 1000

            # Log error
            logger.error(
                "request_failed",
                method=request.method,
                path=request.url.path,
                latency_ms=round(latency_ms, 2),
                error=str(exc),
                exc_info=True,
            )
            raise
