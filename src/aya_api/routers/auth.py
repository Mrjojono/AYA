"""Authentication routes for anonymous device sessions."""

from typing import Annotated, ClassVar

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict

from aya_api.security import (
    InvalidTokenError,
    issue_device_session,
    refresh_device_session,
    verify_access_token,
)

router = APIRouter(prefix="/auth", tags=["auth"])


class SessionResponse(BaseModel):
    """Issued anonymous device session."""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True)

    access_token: str
    refresh_token: str
    token_type: str = "bearer"  # noqa: S105


class RefreshRequest(BaseModel):
    """Refresh token payload."""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True)

    refresh_token: str


@router.post("/anonymous", status_code=status.HTTP_201_CREATED)
async def create_anonymous_session() -> SessionResponse:
    """Open the application with a device-linked anonymous session."""
    pair = issue_device_session()
    return SessionResponse(
        access_token=pair.access_token,
        refresh_token=pair.refresh_token,
    )


@router.post("/refresh")
async def refresh_session(payload: RefreshRequest) -> SessionResponse:
    """Rotate a refresh token into a new session."""
    try:
        pair = refresh_device_session(payload.refresh_token)
    except InvalidTokenError as exc:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, str(exc)) from exc
    return SessionResponse(
        access_token=pair.access_token,
        refresh_token=pair.refresh_token,
    )


DeviceId = Annotated[str, Depends(verify_access_token)]


@router.get("/me")
async def read_session(device_id: DeviceId) -> dict[str, str]:
    """Report the device behind the current access token."""
    return {"device_id": device_id}
