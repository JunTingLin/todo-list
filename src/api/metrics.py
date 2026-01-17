"""Metrics endpoint for Prometheus."""

from fastapi import APIRouter, Response
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

router = APIRouter(tags=["metrics"])


@router.get("/metrics")
async def metrics():
    """
    Prometheus 指標端點

    暴露 Prometheus 格式的系統指標:
    - http_requests_total: HTTP 請求總次數
    - http_request_duration_seconds: HTTP 請求延遲分布

    指標使用低基數標籤 (method, path, status) 避免高基數問題。
    """
    # Generate Prometheus metrics in text format
    metrics_output = generate_latest()

    return Response(content=metrics_output, media_type=CONTENT_TYPE_LATEST)
