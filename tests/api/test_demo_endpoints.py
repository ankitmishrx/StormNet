"""Integration tests for Demo & Replay FastAPI endpoints."""

from fastapi.testclient import TestClient
from apps.api.main import app

client = TestClient(app)


def test_get_demo_status_endpoint():
    """Verifies GET /api/v1/demo/status returns demo scenarios with explicit non-operational flags."""
    response = client.get("/api/v1/demo/status")
    assert response.status_code == 200

    data = response.json()
    assert data["mode"] == "DEMO_REPLAY"
    assert data["is_operational"] is False
    assert "MUST NOT" in data["disclaimer"]
    assert len(data["supported_scenarios"]) >= 2

    for scenario in data["supported_scenarios"]:
        assert scenario["type"] in ["SYNTHETIC_DATA", "SAMPLE_DATA", "REPLAY_DATA"]


def test_get_demo_scenario_endpoint():
    """Verifies GET /api/v1/demo/scenario/{id} returns scenario frames with watermarking."""
    response = client.get("/api/v1/demo/scenario/delhi-squall-sim")
    assert response.status_code == 200

    data = response.json()
    assert data["scenario_id"] == "delhi-squall-sim"
    assert data["is_operational"] is False
    assert data["data_provenance"] == "SYNTHETIC_DATA"
    assert "DEMONSTRATION ONLY" in data["watermark"]
    assert len(data["frames"]) == 3


def test_get_demo_scenario_not_found():
    """Verifies 404 for unknown scenario ID."""
    response = client.get("/api/v1/demo/scenario/nonexistent-scenario")
    assert response.status_code == 404
