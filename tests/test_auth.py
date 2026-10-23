"""Tests for anonymous device sessions."""

from http import HTTPStatus

import pytest
from httpx import ASGITransport, AsyncClient

from aya_api.main import create_app
from aya_api.security import (
    InvalidTokenError,
    verify_access_token,
)


@pytest.mark.anyio
async def test_anonymous_session_issues_tokens() -> None:
    transport = ASGITransport(app=create_app())
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/auth/anonymous")

    assert response.status_code == HTTPStatus.CREATED
    body: dict[str, str] = response.json()
    assert body["access_token"]
    assert body["refresh_token"]
    device_id = verify_access_token(body["access_token"])
    assert device_id


@pytest.mark.anyio
async def test_expired_access_token_is_rejected() -> None:
    # An invalid token must be rejected.
    with pytest.raises(InvalidTokenError):
        _ = verify_access_token("not-a-token")


@pytest.mark.anyio
async def test_refresh_rotates_session() -> None:
    transport = ASGITransport(app=create_app())
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        created = await client.post("/auth/anonymous")
        created_body: dict[str, str] = created.json()
        refresh_token = created_body["refresh_token"]
        refreshed = await client.post(
            "/auth/refresh", json={"refresh_token": refresh_token}
        )

    assert refreshed.status_code == HTTPStatus.OK
    assert refreshed.json()["access_token"]
