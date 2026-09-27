"""Unit & Integration Tests for Multi-Source Meteorological Data Fusion Pipeline."""

import os
import pytest
from datetime import datetime, timezone, timedelta
from pathlib import Path

from ml.preprocessing.fusion import (
    SatelliteAdapter,
    LightningAdapter,
    AtmosphericAdapter,
    TemporalAligner,
    TemporalLeakageError,
    LightningGridAggregator,
    MultiSourceFusionEngine,
    FeatureDatasetExporter,
    QualityFlag,
    DataFreshnessTier,
    SatelliteObservation,
    LightningObservation,
    AtmosphericObservation,
)
from ml.preprocessing.radar.grid import CommonGridGenerator


@pytest.fixture
def sample_timestamps():
    anchor = datetime(2026, 9, 26, 10, 15, 0, tzinfo=timezone.utc)
    return {
        "anchor": anchor,
        "valid_past": anchor - timedelta(minutes=2),
        "valid_start": anchor - timedelta(minutes=5),
        "future_leak": anchor + timedelta(minutes=1),
    }


@pytest.fixture
def sample_grid_cells():
    grid_gen = CommonGridGenerator(grid_size_km=3.0, bbox=(76.5, 28.0, 77.8, 29.2))
    lats, lons = grid_gen.get_lat_lon_mesh()
    cells = []
    # Use small subset for fast tests
    for j in range(min(5, len(lats))):
        for i in range(min(5, len(lons))):
            cells.append({
                "grid_id": grid_gen.generate_cell_id(i, j),
                "center_lat": float(lats[j]),
                "center_lon": float(lons[i]),
            })
    return cells


def test_satellite_normalization():
    adapter = SatelliteAdapter()
    file_path = "data/samples/satellite/insat_3dr_delhi_20260926_1545.json"
    observations = adapter.load_from_file(file_path)

    assert len(observations) == 4
    for obs in observations:
        assert obs.satellite_id == "INSAT-3DR"
        assert obs.channel == "TIR1_10.8UM"
        assert 150.0 <= obs.brightness_temp_kelvin <= 350.0
        assert obs.quality_flag == QualityFlag.VALID


def test_satellite_invalid_bounds_quarantined():
    adapter = SatelliteAdapter()
    invalid_obs = [
        SatelliteObservation(
            satellite_id="INSAT-3DR",
            timestamp=datetime.now(timezone.utc),
            latitude=28.6,
            longitude=77.2,
            brightness_temp_kelvin=999.0,  # Physically impossible Kelvin
        )
    ]
    validated = adapter.validate_observations(invalid_obs)
    assert validated[0].brightness_temp_kelvin is None
    assert validated[0].quality_flag == QualityFlag.INVALID


def test_lightning_normalization():
    adapter = LightningAdapter()
    file_path = "data/samples/lightning/lln_delhi_20260926_1545.json"
    strikes = adapter.load_from_file(file_path)

    assert len(strikes) == 5
    for s in strikes:
        assert s.network_id == "IITM_NCR_LLN"
        assert s.strike_type in ["CG", "IC"]
        assert -500.0 <= s.peak_current_ka <= 500.0
        assert s.quality_flag == QualityFlag.VALID


def test_atmospheric_normalization():
    adapter = AtmosphericAdapter()
    file_path = "data/samples/aws/aws_delhi_20260926_1545.json"
    stations = adapter.load_from_file(file_path)

    assert len(stations) == 4
    for stn in stations:
        assert -40.0 <= stn.temperature_celsius <= 60.0
        assert 0.0 <= stn.relative_humidity_pct <= 100.0
        assert stn.quality_flag == QualityFlag.VALID


def test_temporal_alignment_causal_leakage_prevention(sample_timestamps):
    aligner = TemporalAligner(default_window_seconds=300, strict_causal=True)
    window = aligner.create_window(sample_timestamps["anchor"], duration_seconds=300)

    # Observation from the future relative to window anchor
    future_obs = [
        LightningObservation(
            event_id="LTG-LEAK-01",
            timestamp=sample_timestamps["future_leak"],
            latitude=28.6,
            longitude=77.2,
        )
    ]

    with pytest.raises(TemporalLeakageError, match="Temporal Leakage Violation"):
        aligner.filter_and_align(future_obs, window)


def test_temporal_alignment_valid_window(sample_timestamps):
    aligner = TemporalAligner(default_window_seconds=300, strict_causal=True)
    window = aligner.create_window(sample_timestamps["anchor"], duration_seconds=300)

    valid_obs = [
        LightningObservation(
            event_id="LTG-VAL-01",
            timestamp=sample_timestamps["valid_past"],
            latitude=28.6,
            longitude=77.2,
        ),
        LightningObservation(
            event_id="LTG-VAL-02",
            timestamp=sample_timestamps["valid_start"],
            latitude=28.6,
            longitude=77.2,
        ),
    ]

    aligned = aligner.filter_and_align(valid_obs, window)
    assert len(aligned) == 2


def test_lightning_grid_aggregation(sample_timestamps, sample_grid_cells):
    aggregator = LightningGridAggregator(grid_size_km=3.0)
    window = TemporalAligner().create_window(sample_timestamps["anchor"], duration_seconds=300)

    # Strike exactly at center of first cell
    target_cell = sample_grid_cells[0]
    strikes = [
        LightningObservation(
            event_id="LTG-001",
            timestamp=sample_timestamps["valid_past"],
            latitude=target_cell["center_lat"],
            longitude=target_cell["center_lon"],
        ),
        LightningObservation(
            event_id="LTG-002",
            timestamp=sample_timestamps["valid_past"],
            latitude=target_cell["center_lat"],
            longitude=target_cell["center_lon"],
        ),
    ]

    result = aggregator.aggregate_to_grid(strikes, sample_grid_cells, window)
    target_metrics = result[target_cell["grid_id"]]

    assert target_metrics["strike_count"] == 2
    assert target_metrics["density_per_km2"] == round(2.0 / 9.0, 4)
    assert target_metrics["rate_per_min"] == round(2.0 / 5.0, 2)
    assert target_metrics["trend"] == "INCREASING"


def test_multi_source_fusion_all_sources(sample_timestamps, sample_grid_cells):
    engine = MultiSourceFusionEngine(grid_size_km=3.0, window_duration_seconds=300)

    radar_obs = [{
        "grid_id": sample_grid_cells[0]["grid_id"],
        "reflectivity_dbz": 55.4,
        "max_dbz": 58.0,
    }]
    sat_obs = [
        SatelliteObservation(
            satellite_id="INSAT-3DR",
            timestamp=sample_timestamps["valid_past"],
            latitude=28.6,
            longitude=77.2,
            brightness_temp_kelvin=215.0,
            cooling_rate_kelvin_per_hour=-12.0,
        )
    ]
    ltg_obs = [
        LightningObservation(
            event_id="LTG-001",
            timestamp=sample_timestamps["valid_past"],
            latitude=sample_grid_cells[0]["center_lat"],
            longitude=sample_grid_cells[0]["center_lon"],
        )
    ]
    aws_obs = [
        AtmosphericObservation(
            station_id="AWS-DEL-SAF",
            timestamp=sample_timestamps["valid_past"],
            latitude=28.58,
            longitude=77.20,
            temperature_celsius=33.5,
            relative_humidity_pct=75.0,
        )
    ]

    frame = engine.fuse_frame(
        anchor_timestamp=sample_timestamps["anchor"],
        grid_cells=sample_grid_cells,
        radar_grid_observations=radar_obs,
        satellite_observations=sat_obs,
        lightning_observations=ltg_obs,
        atmospheric_observations=aws_obs,
        is_sample=True,
    )

    assert frame.radar_available is True
    assert frame.satellite_available is True
    assert frame.lightning_available is True
    assert frame.atmospheric_available is True
    assert frame.completeness_score == 1.0
    assert frame.data_freshness == DataFreshnessTier.SAMPLE
    assert len(frame.cells) == len(sample_grid_cells)

    # Inspect cell 0
    c0 = frame.cells[0]
    assert c0.radar_reflectivity_dbz == 55.4
    assert c0.satellite_brightness_temp_k == 215.0
    assert c0.lightning_strike_count == 1
    assert c0.atmospheric_temp_c == 33.5


def test_multi_source_fusion_missing_sources_graceful_degradation(sample_timestamps, sample_grid_cells):
    engine = MultiSourceFusionEngine(grid_size_km=3.0, window_duration_seconds=300)

    # Only radar available, satellite and lightning are None
    radar_obs = [{
        "grid_id": sample_grid_cells[0]["grid_id"],
        "reflectivity_dbz": 45.0,
    }]

    frame = engine.fuse_frame(
        anchor_timestamp=sample_timestamps["anchor"],
        grid_cells=sample_grid_cells,
        radar_grid_observations=radar_obs,
        satellite_observations=None,
        lightning_observations=None,
        atmospheric_observations=None,
        is_sample=True,
    )

    assert frame.radar_available is True
    assert frame.satellite_available is False
    assert frame.lightning_available is False
    assert frame.atmospheric_available is False
    assert frame.completeness_score == 0.25

    c0 = frame.cells[0]
    assert c0.radar_reflectivity_dbz == 45.0
    # Missing variables are strictly None, not fabricated
    assert c0.satellite_brightness_temp_k is None
    assert c0.satellite_quality == QualityFlag.UNAVAILABLE
    assert c0.lightning_quality == QualityFlag.UNAVAILABLE
    assert c0.atmospheric_temp_c is None
    assert c0.atmospheric_quality == QualityFlag.UNAVAILABLE


def test_feature_dataset_export_parquet(sample_timestamps, sample_grid_cells, tmp_path):
    engine = MultiSourceFusionEngine(grid_size_km=3.0)
    frame = engine.fuse_frame(
        anchor_timestamp=sample_timestamps["anchor"],
        grid_cells=sample_grid_cells,
    )

    exporter = FeatureDatasetExporter(output_base_dir=str(tmp_path))
    meta = exporter.export_frame(frame)

    assert os.path.exists(meta["data_file"])
    assert meta["record_count"] == len(sample_grid_cells)
    assert meta["format"] in ["parquet", "json"]

    if meta["format"] == "parquet":
        import pyarrow.parquet as pq
        tbl = pq.read_table(meta["data_file"])
        assert tbl.num_rows == len(sample_grid_cells)
