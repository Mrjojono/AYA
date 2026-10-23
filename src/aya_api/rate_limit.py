"""Per-client rate limiting middleware."""

import time
from collections import defaultdict, deque
from typing import Final, override

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.types import ASGIApp

_WINDOW_SECONDS: Final[int] = 60
_MAX_REQUESTS: Final[int] = 60


class RateLimiter:
    """Sliding-window rate limiter keyed by client identity."""

    def __init__(
        self, max_requests: int = _MAX_REQUESTS, window_seconds: int = _WINDOW_SECONDS
    ) -> None:
        """Initialize the sliding-window limiter."""
        self._max_requests: int = max_requests
        self._window_seconds: int = window_seconds
        self._buckets: defaultdict[str, deque[float]] = defaultdict(deque)

    def allow(self, key: str) -> bool:
        """Return whether ``key`` may make another request now."""
        now = time.monotonic()
        bucket = self._buckets[key]
        cutoff = now - self._window_seconds
        while bucket and bucket[0] <= cutoff:
            _ = bucket.popleft()
        if len(bucket) >= self._max_requests:
            return False
        bucket.append(now)
        return True


class RateLimitMiddleware(BaseHTTPMiddleware):  # type: ignore[misc]
    """Reject requests that exceed the configured per-client limit."""

    def __init__(self, app: ASGIApp, limiter: RateLimiter | None = None) -> None:  # type: ignore[override]
        """Initialize the middleware with an optional limiter."""
        super().__init__(app)  # type: ignore[arg-type]
        self._limiter: RateLimiter = limiter or RateLimiter()

    @override
    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        """Apply the rate limit to the incoming request."""
        """Apply the rate limit to the incoming request."""
        key = request.client.host if request.client is not None else "anonymous"
        if not self._limiter.allow(key):
            return JSONResponse(
                status_code=429,
                content={"detail": "rate limit exceeded"},
            )
        return await call_next(request)
