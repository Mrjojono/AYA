"""Smoke tests for core endpoints."""

from fastapi.testclient import TestClient

from aya_api.main import create_app


def test_health_smoke() -> None:
    client = TestClient(create_app())
    response = client.get("/health")
    assert response.status_code == 200  # noqa: PLR2004
    assert response.json()["status"] == "ok"


def test_medications_search_smoke() -> None:
    client = TestClient(create_app())
    response = client.get("/medications/search", params={"q": "para"})
    assert response.status_code == 200  # noqa: PLR2004
    assert isinstance(response.json(), list)
