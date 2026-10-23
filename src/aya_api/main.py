"""HTTP application factory and system endpoints."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import ClassVar

from fastapi import FastAPI
from pydantic import BaseModel, ConfigDict

from aya_api.db import engine
from aya_api.logging import configure_logging
from aya_api.rate_limit import RateLimitMiddleware
from aya_api.routers import auth

configure_logging()


class HealthResponse(BaseModel):
    """Public service health contract."""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True)

    status: str


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncGenerator[None]:
    """Dispose pooled resources when the API stops."""
    yield
    await engine.dispose()


def create_app() -> FastAPI:
    """Build the AYA HTTP API."""
    application = FastAPI(title="AYA API", version="0.1.0", lifespan=lifespan)

    application.add_middleware(RateLimitMiddleware)

    @application.get("/health", tags=["system"])
    async def health() -> HealthResponse:
        """Report that the HTTP service accepts requests."""
        return HealthResponse(status="ok")

    application.include_router(auth.router)
    return application


app = create_app()
