"""Unit tests for the Radar Ingestion, Validation, Georeferencing, and Gridding Pipeline."""

import os
from datetime import datetime, timezone, timedelta
import numpy as np
import pytest

from ml.preprocessing.radar.interfaces import RadarObservation, RadarSweep, RadarVolume
from ml.preprocessing.radar.validator import (
    RadarValidator,
    RadarValidationError,
    CorruptedDataError,
    InvalidCoordinateError,
)
from ml.preprocessing.radar.georeference import (
    polar_to_ground_range,
    radar_bin_to_latlon,
    compute_radar_coverage_polygon,
    create_bbox_polygon,
)
from ml.preprocessing.radar.grid import CommonGridGenerator
from ml.preprocessing.radar.processors import ReflectivityProcessor
from ml.preprocessing.radar.ingest import process_radar_ingestion, parse_radar_file


def test_radar_validation_timestamp():
    """Verifies timestamp validation rules."""
    valid_ts = datetime.now(timezone.utc) - timedelta(minutes=5)
    RadarValidator.validate_timestamp(valid_ts)

    # Future timestamp should fail for live mode
    future_ts = datetime.now(timezone.utc) + timedelta(minutes=45)
    with pytest.raises(RadarValidationError, match="in the future"):
        RadarValidator.validate_timestamp(future_ts, is_sample=False)

    # But sample mode should allow demonstration timestamps
    RadarValidator.validate_timestamp(future_ts, is_sample=True)


def test_radar_validation_coordinates():
    """Verifies antenna and geographic coordinate validation."""
    RadarValidator.validate_coordinates(28.5847, 77.2069, 216.0)

    with pytest.raises(InvalidCoordinateError):
        RadarValidator.validate_coordinates(95.0, 77.0)  # Invalid lat > 90

    with pytest.raises(InvalidCoordinateError):
        RadarValidator.validate_coordinates(28.0, 195.0)  # Invalid lon > 180


def test_radar_validation_bounding_box():
    """Verifies bounding box validation."""
    RadarValidator.validate_bounding_box((76.5, 28.0, 77.8, 29.2))

    with pytest.raises(InvalidCoordinateError):
        RadarValidator.validate_bounding_box((77.8, 28.0, 76.5, 29.2))  # min_lon > max_lon


def test_radar_validation_grid_quarantine():
    """Verifies that corrupted matrices with excessive NaNs are quarantined."""
    # 90% NaN array
    corrupted = np.full((50, 50), np.nan)
    corrupted[:5, :5] = 30.0

    with pytest.raises(CorruptedDataError, match="Data quarantine triggered"):
        RadarValidator.validate_reflectivity_grid(corrupted)


def test_radar_georeference_polar_to_ground():
    """Verifies curved Earth 4/3 effective radius calculations."""
    slant_r = 100.0  # km
    elev = 1.5  # degrees

    ground_s, height_h = polar_to_ground_range(slant_r, elev)
    assert 95.0 < ground_s < 100.0
    assert height_h > 2.0  # Height above antenna in km


def test_radar_georeference_latlon_transformation():
    """Verifies transformation from antenna distance/azimuth to geographic coordinates."""
    antenna_lat = 28.5847
    antenna_lon = 77.2069

    # Due North 50 km
    lat_n, lon_n = radar_bin_to_latlon(antenna_lat, antenna_lon, 50.0, 0.0)
    assert lat_n > antenna_lat
    assert abs(lon_n - antenna_lon) < 0.01

    # Due East 50 km
    lat_e, lon_e = radar_bin_to_latlon(antenna_lat, antenna_lon, 50.0, 90.0)
    assert lon_e > antenna_lon


def test_common_grid_generator_dimensions():
    """Verifies grid generation at 1 km, 2 km, and 3 km resolutions."""
    bbox = (76.50, 28.00, 77.80, 29.20)

    # 3 km target grid
    grid_3km = CommonGridGenerator(grid_size_km=3.0, bbox=bbox, sector_id="delhi-ncr")
    n_lats_3, n_lons_3 = grid_3km.get_grid_dimensions()
    assert 40 <= n_lats_3 <= 50
    assert 40 <= n_lons_3 <= 50

    cell_id = grid_3km.generate_cell_id(10, 15)
    assert cell_id == "DEL-3KM-X010-Y015"

    poly = grid_3km.get_cell_polygon(10, 15)
    assert poly.is_valid
    assert poly.area > 0

    # 1 km target grid
    grid_1km = CommonGridGenerator(grid_size_km=1.0, bbox=bbox, sector_id="delhi-ncr")
    n_lats_1, n_lons_1 = grid_1km.get_grid_dimensions()
    assert n_lats_1 > n_lats_3 * 2.5


def test_reflectivity_clutter_filter():
    """Verifies that non-meteorological noise (<12 dBZ) is suppressed."""
    raw = np.array([[5.0, 15.0], [25.0, 8.0]])
    filtered = ReflectivityProcessor.filter_ground_clutter(raw)

    assert filtered[0, 0] == 0.0
    assert filtered[0, 1] == 15.0
    assert filtered[1, 0] == 25.0
    assert filtered[1, 1] == 0.0


def test_reflectivity_vector_contours():
    """Verifies that vector contours are extracted properly for web mapping."""
    lats = np.array([28.60, 28.63, 28.66])
    lons = np.array([77.20, 77.23, 77.26])
    matrix = np.array([
        [25.0, 40.0, 50.0],
        [30.0, 58.0, 62.0],
        [20.0, 35.0, 45.0],
    ])

    contours = ReflectivityProcessor.extract_reflectivity_contours(matrix, lats, lons, dbz_levels=[20, 35, 55])
    assert len(contours) >= 2
    levels = [c["dbz_level"] for c in contours]
    assert 20 in levels
    assert 35 in levels


def test_ingestion_cli_execution():
    """Verifies the complete ingestion pipeline on the sample radar dataset."""
    sample_file = "data/samples/radar/dwr_delhi_20260926_1545.json"
    assert os.path.exists(sample_file)

    summary = process_radar_ingestion(sample_file, target_grid_km=3.0, sector_id="delhi-ncr")

    assert summary["radar_id"] == "DWR-DEL-SAF"
    assert summary["source"] == "DEVELOPMENT_SAMPLE"
    assert summary["target_grid_km"] == 3.0
    assert summary["cells_processed"] == 20
    assert summary["invalid_cells"] == 0
    assert summary["max_reflectivity_dbz"] >= 60.0
    assert summary["vector_contour_levels"] >= 3
