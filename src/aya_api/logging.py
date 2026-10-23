"""Structured logging with personal-data redaction."""

import contextlib
import json
import logging
from collections.abc import Mapping
from typing import Final, override

_SENSITIVE_KEYS: Final[frozenset[str]] = frozenset(
    {
        "email",
        "name",
        "phone",
        "address",
        "health",
        "symptom",
        "meal",
        "password",
        "token",
        "access_token",
        "refresh_token",
        "device_id",
        "user_id",
    }
)

_REDACTED: Final[str] = "[REDACTED]"


def redact(value: object) -> object:
    """Return a copy of ``value`` with sensitive fields replaced."""
    if isinstance(value, Mapping):
        result: dict[object, object] = {}
        for key, item in value.items():
            result[key] = (
                _REDACTED if str(key).lower() in _SENSITIVE_KEYS else redact(item)
            )
        return result
    if isinstance(value, list):
        return [redact(item) for item in value]
    if isinstance(value, tuple):
        return [redact(item) for item in value]
    return value


class RedactingFilter(logging.Filter):
    """Filter that redacts sensitive fields from log records."""

    @override
    def filter(self, record: logging.LogRecord) -> bool:
        """Redact sensitive data before the record is emitted."""
        if isinstance(record.msg, str) and record.args:
            with contextlib.suppress(TypeError, ValueError):
                record.args = tuple(redact(arg) for arg in record.args)
        if isinstance(record.msg, Mapping):
            record.msg = redact(record.msg)  # type: ignore[assignment]
        return True


def configure_logging() -> None:
    """Install the redacting filter on the root logger."""
    root = logging.getLogger()
    if not any(isinstance(f, RedactingFilter) for f in root.filters):
        root.addFilter(RedactingFilter())


def to_json(record: logging.LogRecord) -> str:
    """Render a log record as a single JSON line with redacted fields."""
    payload = {
        "level": record.levelname,
        "logger": record.name,
        "message": record.getMessage(),
    }
    return json.dumps(redact(payload))
