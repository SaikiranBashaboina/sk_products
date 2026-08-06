"""Request logging middleware for monitoring and debugging."""

import time
import logging
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger("api.request")


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to log all HTTP requests with timing."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        request_id = request.headers.get("X-Request-ID", "-")

        # Log incoming request
        logger.info(
            "[%s] → %s %s",
            request_id,
            request.method,
            request.url.path,
        )

        try:
            response = await call_next(request)
            process_time = (time.time() - start_time) * 1000

            logger.info(
                "[%s] ← %s %s - %d (%dms)",
                request_id,
                request.method,
                request.url.path,
                response.status_code,
                process_time,
            )

            # Add timing header
            response.headers["X-Process-Time-MS"] = str(int(process_time))
            response.headers["X-Request-ID"] = request_id

            return response
        except Exception as exc:
            process_time = (time.time() - start_time) * 1000
            logger.error(
                "[%s] ✗ %s %s - ERROR (%dms): %s",
                request_id,
                request.method,
                request.url.path,
                process_time,
                str(exc),
            )
            raise