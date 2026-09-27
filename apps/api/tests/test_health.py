"""Tests for the root health check endpoint."""

from fastapi.testclient import TestClient


def test_health_check_returns_200(client: TestClient):
    """Verifies GET /health returns 200 OK and expected diagnostic schema."""
    response = client.get("/health")
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "HEALTHY"
    assert "version" in data
    assert "timestamp" in data
    assert data["services"]["api"] == "OPERATIONAL"
