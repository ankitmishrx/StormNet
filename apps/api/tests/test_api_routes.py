"""Unit tests verifying all /api/v1 routes."""

from fastapi.testclient import TestClient


def test_get_storms_endpoint(client: TestClient):
    """Verifies GET /api/v1/storms returns valid storm list."""
    response = client.get("/api/v1/storms")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    first_storm = data[0]
    assert "cell_code" in first_storm
    assert "severity_level" in first_storm
    assert "max_reflectivity_dbz" in first_storm


def test_get_storm_by_id_endpoint(client: TestClient):
    """Verifies GET /api/v1/storms/{id} returns detailed diagnostics and track vectors."""
    test_id = "11111111-1111-1111-1111-111111111111"
    response = client.get(f"/api/v1/storms/{test_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_id
    assert "tracks" in data
    assert len(data["tracks"]) > 0


def test_get_forecasts_timeline_endpoint(client: TestClient):
    """Verifies GET /api/v1/forecasts returns 0-6 hour steps."""
    response = client.get("/api/v1/forecasts?sector_id=delhi-ncr")
    assert response.status_code == 200
    data = response.json()
    assert data["sector_id"] == "delhi-ncr"
    assert "frames" in data
    assert len(data["frames"]) > 0
    first_frame = data["frames"][0]
    assert "confidence_index" in first_frame
    assert "lead_time_minutes" in first_frame


def test_get_hazards_endpoint(client: TestClient):
    """Verifies GET /api/v1/hazards returns 4 core hazard cards."""
    response = client.get("/api/v1/hazards")
    assert response.status_code == 200
    cards = response.json()
    assert isinstance(cards, list)
    hazard_types = [c["hazard_type"] for c in cards]
    assert "CLOUDBURST" in hazard_types
    assert "HAIL" in hazard_types
    assert "SQUALL" in hazard_types
    assert "LIGHTNING" in hazard_types


def test_get_alerts_endpoint(client: TestClient):
    """Verifies GET /api/v1/alerts returns active CAP warnings."""
    response = client.get("/api/v1/alerts")
    assert response.status_code == 200
    alerts = response.json()
    assert isinstance(alerts, list)
    if len(alerts) > 0:
        first_alert = alerts[0]
        assert "alert_identifier" in first_alert
        assert "headline" in first_alert
        assert first_alert["severity"] in ["YELLOW", "ORANGE", "RED", "GREEN"]


def test_get_locations_endpoint(client: TestClient):
    """Verifies GET /api/v1/locations returns reference sites."""
    response = client.get("/api/v1/locations")
    assert response.status_code == 200
    locations = response.json()
    assert isinstance(locations, list)
    assert len(locations) > 0
    names = [loc["name"] for loc in locations]
    assert any("Safdarjung" in n for n in names)
