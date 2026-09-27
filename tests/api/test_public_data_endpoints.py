"""Integration tests for Public Meteorological Data FastAPI endpoints."""

from fastapi.testclient import TestClient
from apps.api.main import app

client = TestClient(app)


def test_get_public_data_status_endpoint():
    """Verifies GET /api/v1/public-data/status returns public dataset metadata and grid dimensions."""
    response = client.get("/api/v1/public-data/status")
    assert response.status_code == 200

    data = response.json()
    assert data["dataset_id"] == "pub_noaa_isd_vidp_delhi_2024"
    assert data["provider"] == "NOAA NCEI"
    assert data["provenance"] == "PUBLIC_REAL_DATA"
    assert data["is_operational"] is False
    assert "HISTORICAL PUBLIC DATA" in data["watermark"]
    assert "air_temperature_celsius" in data["available_variables"]
    assert "45 x 43" in data["target_grid_dimensions"]
    assert data["coverage"]["station_id"] == "42181099999"
    assert data["coverage"]["domain"] == "Delhi NCR, India"


def test_get_public_data_sample_record_endpoint():
    """Verifies GET /api/v1/public-data/sample-record returns verified real observation values."""
    response = client.get("/api/v1/public-data/sample-record")
    assert response.status_code == 200

    data = response.json()
    assert data["dataset_id"] == "pub_noaa_isd_vidp_delhi_2024"
    assert data["provenance"] == "PUBLIC_REAL_DATA"
    assert data["is_operational"] is False
    assert data["watermark"] == "HISTORICAL PUBLIC DATA"
    assert data["air_temperature_c"] == 28.4
    assert data["dewpoint_c"] == 26.2
    assert "target_grid_coord" in data
