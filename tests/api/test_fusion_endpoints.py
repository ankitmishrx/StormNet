"""API Integration Tests for Multi-Source Fusion Endpoints."""

import pytest
from fastapi.testclient import TestClient
from apps.api.main import app

client = TestClient(app)


def test_get_fusion_latest_endpoint():
    response = client.get("/api/v1/fusion/latest?sector_id=delhi-ncr")
    assert response.status_code == 200
    data = response.json()

    assert "id" in data
    assert data["sector_id"] == "delhi-ncr"
    assert "timestamp" in data
    assert "completeness_score" in data
    assert "cells" in data
    assert data["total_cells"] > 0
    assert data["data_freshness"] in ["SAMPLE", "LIVE", "HISTORICAL"]

    cell0 = data["cells"][0]
    assert "grid_id" in cell0
    assert "radar_reflectivity_dbz" in cell0
    assert "satellite_brightness_temp_k" in cell0
    assert "lightning_strike_count" in cell0
    assert "atmospheric_temp_c" in cell0


def test_get_fusion_status_endpoint():
    response = client.get("/api/v1/fusion/status?sector_id=delhi-ncr")
    assert response.status_code == 200
    data = response.json()

    assert data["sector_id"] == "delhi-ncr"
    assert data["active_sources_count"] >= 1
    assert data["total_sources_count"] == 4
    assert 0.0 <= data["network_completeness_ratio"] <= 1.0
    assert "sources" in data
    assert len(data["sources"]) == 4


def test_get_fusion_sources_endpoint():
    response = client.get("/api/v1/fusion/sources")
    assert response.status_code == 200
    sources = response.json()

    assert isinstance(sources, list)
    types = [s["source_type"] for s in sources]
    assert "RADAR" in types
    assert "SATELLITE" in types
    assert "LIGHTNING" in types
    assert "AWS" in types


def test_get_fusion_grid_cell_history_endpoint():
    response = client.get("/api/v1/fusion/grid/GRID-NCR-001?limit=5")
    assert response.status_code == 200
    data = response.json()

    assert data["grid_id"] == "GRID-NCR-001"
    assert "history" in data
    assert len(data["history"]) >= 1


def test_get_fusion_frame_by_timestamp_valid():
    response = client.get("/api/v1/fusion/2026-09-26T10:15:00Z?sector_id=delhi-ncr")
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert "timestamp" in data


def test_get_fusion_frame_by_timestamp_invalid():
    response = client.get("/api/v1/fusion/invalid-timestamp-format")
    assert response.status_code == 400
    assert "Invalid timestamp format" in response.json()["detail"]
