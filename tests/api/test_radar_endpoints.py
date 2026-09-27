"""Integration tests for Doppler Weather Radar FastAPI endpoints."""

from fastapi.testclient import TestClient
from apps.api.main import app

client = TestClient(app)


def test_get_radar_latest_endpoint():
    """Verifies GET /api/v1/radar/latest returns valid radar frame metadata and contours."""
    response = client.get("/api/v1/radar/latest")
    assert response.status_code == 200

    data = response.json()
    assert "id" in data
    assert data["radar_id"] == "DWR-DEL-SAF"
    assert data["product_type"] == "COMPOSITE_REFLECTIVITY"
    assert data["resolution_km"] == 3.0
    assert data["crs"] == "EPSG:4326"
    assert len(data["bounding_box"]) == 4
    assert data["max_dbz"] >= 60.0
    assert data["data_freshness"] in ["SAMPLE", "LIVE"]
    assert "contours" in data


def test_get_radar_frames_endpoint():
    """Verifies GET /api/v1/radar/frames lists chronological frames."""
    response = client.get("/api/v1/radar/frames?limit=5")
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert "radar_id" in data[0]


def test_get_radar_status_endpoint():
    """Verifies GET /api/v1/radar/status returns data freshness and operational health."""
    response = client.get("/api/v1/radar/status?radar_id=DWR-DEL-SAF")
    assert response.status_code == 200

    data = response.json()
    assert data["radar_id"] == "DWR-DEL-SAF"
    assert data["status"] in ["LIVE", "HISTORICAL", "SAMPLE", "STALE", "UNAVAILABLE"]
    assert "last_observation_time" in data
    assert "disclaimer" in data


def test_get_radar_frame_by_id_endpoint():
    """Verifies GET /api/v1/radar/{frame_id} returns detailed frame information."""
    # First get latest frame ID
    latest = client.get("/api/v1/radar/latest").json()
    frame_id = latest["id"]

    response = client.get(f"/api/v1/radar/{frame_id}")
    assert response.status_code == 200

    data = response.json()
    assert data["id"] == frame_id
    assert data["radar_id"] == "DWR-DEL-SAF"


def test_get_radar_grid_endpoint():
    """Verifies GET /api/v1/radar/{frame_id}/grid returns gridded cell observations."""
    latest = client.get("/api/v1/radar/latest").json()
    frame_id = latest["id"]

    response = client.get(f"/api/v1/radar/{frame_id}/grid")
    assert response.status_code == 200

    data = response.json()
    assert data["frame_id"] == frame_id
    assert "cells" in data
    assert data["cells_count"] >= 1
    assert "reflectivity_dbz" in data["cells"][0]
