from http import HTTPStatus

import pytest
from httpx import ASGITransport, AsyncClient

from aya_api.main import create_app


@pytest.mark.anyio
async def test_health_reports_service_availability() -> None:
    transport = ASGITransport(app=create_app())

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/health")

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"status": "ok"}
