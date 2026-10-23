"""Anonymous device-linked session tokens."""

import uuid
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Final

import jwt

from aya_api.config import get_settings

_DEVICE_SUBJECT: Final[str] = "device"


@dataclass(frozen=True, slots=True)
class TokenPair:
    """Access and refresh tokens issued for one device."""

    access_token: str
    refresh_token: str
    access_expires_at: datetime
    refresh_expires_at: datetime


def issue_device_session(device_id: str | None = None) -> TokenPair:
    """Issue a limited access token and a refresh token for a device."""
    settings = get_settings()
    now = datetime.now(UTC)
    resolved_device_id = device_id or str(uuid.uuid4())
    access_expires_at = now + timedelta(seconds=settings.access_token_ttl_seconds)
    refresh_expires_at = now + timedelta(seconds=settings.refresh_token_ttl_seconds)

    access_token = jwt.encode(  # type: ignore[no-untyped-call, reportUnknownMemberType]
        {
            "sub": resolved_device_id,
            "type": "access",
            "iat": int(now.timestamp()),
            "exp": int(access_expires_at.timestamp()),
        },
        settings.jwt_secret.get_secret_value(),
        algorithm="HS256",
    )
    refresh_token = jwt.encode(  # type: ignore[no-untyped-call, reportUnknownMemberType]
        {
            "sub": resolved_device_id,
            "type": "refresh",
            "iat": int(now.timestamp()),
            "exp": int(refresh_expires_at.timestamp()),
            "jti": str(uuid.uuid4()),
        },
        settings.jwt_secret.get_secret_value(),
        algorithm="HS256",
    )
    return TokenPair(
        access_token=access_token,
        refresh_token=refresh_token,
        access_expires_at=access_expires_at,
        refresh_expires_at=refresh_expires_at,
    )


class InvalidTokenError(ValueError):
    """Raised when a token cannot be verified or has expired."""


def verify_access_token(token: str) -> str:
    """Return the device id carried by a valid, non-expired access token."""
    settings = get_settings()
    try:
        payload = jwt.decode(  # type: ignore[no-untyped-call, reportUnknownMemberType]
            token,
            settings.jwt_secret.get_secret_value(),
            algorithms=["HS256"],
            options={"require": ["exp", "sub", "type"]},
        )
    except jwt.PyJWTError as exc:
        msg = "invalid or expired access token"
        raise InvalidTokenError(msg) from exc
    if payload.get("type") != "access":
        msg = "token is not an access token"
        raise InvalidTokenError(msg)
    subject = payload.get("sub")
    if not isinstance(subject, str) or not subject:
        msg = "access token has no device subject"
        raise InvalidTokenError(msg)
    return subject


def refresh_device_session(refresh_token: str) -> TokenPair:
    """Exchange a valid refresh token for a new token pair."""
    settings = get_settings()
    try:
        payload = jwt.decode(  # type: ignore[no-untyped-call, reportUnknownMemberType]
            refresh_token,
            settings.jwt_secret.get_secret_value(),
            algorithms=["HS256"],
            options={"require": ["exp", "sub", "type"]},
        )
    except jwt.PyJWTError as exc:
        msg = "invalid or expired refresh token"
        raise InvalidTokenError(msg) from exc
    if payload.get("type") != "refresh":
        msg = "token is not a refresh token"
        raise InvalidTokenError(msg)
    subject = payload.get("sub")
    if not isinstance(subject, str) or not subject:
        msg = "refresh token has no device subject"
        raise InvalidTokenError(msg)
    return issue_device_session(subject)
