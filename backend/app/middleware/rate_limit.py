"""Rate limiting middleware to prevent brute-force attacks."""

import time
import logging
from collections import defaultdict
from typing import Dict, Tuple

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from app.core.config import settings

logger = logging.getLogger(__name__)


class RateLimitEntry:
    """Tracks request count and time window for rate limiting."""

    def __init__(self, max_requests: int, window_seconds: int):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.timestamps: list = []

    def is_allowed(self) -> Tuple[bool, int]:
        """Check if request is allowed. Returns (allowed, retry_after_seconds)."""
        now = time.time()
        cutoff = now - self.window_seconds

        # Remove old timestamps
        self.timestamps = [t for t in self.timestamps if t > cutoff]

        if len(self.timestamps) >= self.max_requests:
            retry_after = int(self.timestamps[0] + self.window_seconds - now)
            return False, max(1, retry_after)

        self.timestamps.append(now)
        return True, 0


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware with per-IP tracking."""

    def __init__(self, app, login_limit: int = None, general_limit: int = None):
        super().__init__(app)
        self.login_limit = login_limit or settings.RATE_LIMIT_LOGIN_PER_MINUTE
        self.general_limit = general_limit or settings.RATE_LIMIT_GENERAL_PER_MINUTE
        self._login_entries: Dict[str, RateLimitEntry] = defaultdict(
            lambda: RateLimitEntry(self.login_limit, 60)
        )
        self._general_entries: Dict[str, RateLimitEntry] = defaultdict(
            lambda: RateLimitEntry(self.general_limit, 60)
        )

    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP from request headers."""
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.client.host if request.client else "unknown"

    async def dispatch(self, request: Request, call_next) -> Response:
        # Skip rate limiting if in debug/testing mode
        if settings.DEBUG or settings.ENVIRONMENT.lower() in ("testing", "development"):
            return await call_next(request)

        client_ip = self._get_client_ip(request)

        # Apply stricter rate limiting to login endpoint
        if request.url.path.endswith("/auth/login"):
            allowed, retry_after = self._login_entries[client_ip].is_allowed()
            if not allowed:
                logger.warning("Rate limit exceeded for login: %s", client_ip)
                return JSONResponse(
                    status_code=429,
                    content={
                        "success": False,
                        "message": f"Too many login attempts. Try again in {retry_after} seconds.",
                        "errors": [],
                        "status_code": 429,
                    },
                    headers={"Retry-After": str(retry_after)},
                )

        # Apply general rate limiting to all other endpoints
        allowed, retry_after = self._general_entries[client_ip].is_allowed()
        if not allowed:
            logger.warning("Rate limit exceeded: %s for %s", client_ip, request.url.path)
            return JSONResponse(
                status_code=429,
                content={
                    "success": False,
                    "message": "Too many requests. Please slow down.",
                    "errors": [],
                    "status_code": 429,
                },
                headers={"Retry-After": str(retry_after)},
            )

        response = await call_next(request)
        return response