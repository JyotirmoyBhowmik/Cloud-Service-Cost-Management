"""
Enterprise Middleware & Global Exception Handlers
Implements Rule 2.3 & 2.4 (Sanitized Error Responses) and Rule 4.2 (Correlation-ID Distributed Tracing).
"""

import time
import uuid
from datetime import datetime, timezone
from typing import Callable
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.exceptions import CloudScopeException
from app.core.logging_config import logger, redact_sensitive_data


class CorrelationIdMiddleware(BaseHTTPMiddleware):
    """
    Extracts or generates an X-Correlation-ID header on incoming HTTP requests.
    Propagates it into the response headers and request state for end-to-end tracing.
    """
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        correlation_id = request.headers.get("X-Correlation-ID") or f"CS-{uuid.uuid4().hex[:12]}"
        request.state.correlation_id = correlation_id

        start_time = time.time()
        response = await call_next(request)
        process_time_ms = round((time.time() - start_time) * 1000, 2)

        response.headers["X-Correlation-ID"] = correlation_id
        response.headers["X-Process-Time-Ms"] = str(process_time_ms)
        
        # Log request outcome
        logger.info(
            f"{request.method} {request.url.path} -> {response.status_code} ({process_time_ms}ms)",
            extra={
                "correlation_id": correlation_id,
                "extra_data": {
                    "method": request.method,
                    "path": request.url.path,
                    "status_code": response.status_code,
                    "latency_ms": process_time_ms,
                }
            }
        )
        return response


async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Global catch-all exception handler.
    Maps all unhandled exceptions to standardized, sanitized JSON response.
    Never leaks internal stack traces, DB credentials, or OS paths to public clients.
    """
    correlation_id = getattr(request.state, "correlation_id", f"CS-{uuid.uuid4().hex[:12]}")
    now_iso = datetime.now(timezone.utc).isoformat()

    if isinstance(exc, CloudScopeException):
        # Known custom domain exception
        logger.warning(
            f"Domain exception on {request.method} {request.url.path}: {exc.message}",
            extra={"correlation_id": correlation_id, "extra_data": exc.details}
        )
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "timestamp": now_iso,
                "status_code": exc.status_code,
                "error_code": exc.error_code,
                "correlation_id": correlation_id,
                "message": redact_sensitive_data(exc.message),
                "details": exc.details,
            }
        )

    # Unexpected internal exception (Rule 2.1 & 2.4)
    logger.exception(
        f"Unhandled system error on {request.method} {request.url.path}: {str(exc)}",
        extra={"correlation_id": correlation_id}
    )

    return JSONResponse(
        status_code=500,
        content={
            "timestamp": now_iso,
            "status_code": 500,
            "error_code": "INTERNAL_SERVER_ERROR",
            "correlation_id": correlation_id,
            "message": "An internal server error occurred. Please contact system administrator with your correlation ID.",
        }
    )
