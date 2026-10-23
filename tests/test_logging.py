"""Tests for personal-data redaction in logs."""

import logging

from aya_api.logging import RedactingFilter, redact


def test_redact_removes_sensitive_fields() -> None:
    payload = {
        "email": "a@b.com",
        "meal": "rice",
        "status": "ok",
        "nested": {"token": "x", "count": 2},
    }
    result = redact(payload)
    assert isinstance(result, dict)
    assert result["email"] == "[REDACTED]"  # type: ignore[index]
    assert result["meal"] == "[REDACTED]"  # type: ignore[index]
    assert result["status"] == "ok"  # type: ignore[index]
    assert result["nested"]["token"] == "[REDACTED]"  # type: ignore[index]  # noqa: S105
    assert result["nested"]["count"] == 2  # type: ignore[index]  # noqa: PLR2004


def test_redacting_filter_does_not_leak() -> None:
    record = logging.LogRecord(
        "t", logging.INFO, "", 0, "msg %s", ({"email": "secret"},), None
    )

    assert RedactingFilter().filter(record) is True
    assert "secret" not in str(record.args)
