"""Tests for per-client rate limiting."""

from aya_api.rate_limit import RateLimiter


def test_rate_limiter_rejects_after_limit() -> None:
    limiter = RateLimiter(max_requests=2, window_seconds=60)
    assert limiter.allow("client") is True
    assert limiter.allow("client") is True
    assert limiter.allow("client") is False
    assert limiter.allow("other") is True
