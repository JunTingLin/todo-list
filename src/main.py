"""FastAPI application entry point."""

from fastapi import FastAPI
from src.middleware.request_id import RequestIDMiddleware
from src.middleware.logging import LoggingMiddleware
from src.middleware.metrics import MetricsMiddleware
from src.api import todos, health, metrics

# Create FastAPI application
app = FastAPI(
    title="TODO API",
    description="具備可觀測性的 RESTful API 待辦事項系統",
    version="1.0.0",
)

# Register middleware (order matters: last added = first executed)
# Execution order: Metrics -> Logging -> RequestID -> Routes
app.add_middleware(MetricsMiddleware)
app.add_middleware(LoggingMiddleware)
app.add_middleware(RequestIDMiddleware)

# Register routers
app.include_router(todos.router)
app.include_router(health.router)
app.include_router(metrics.router)


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "TODO API is running", "version": "1.0.0"}
