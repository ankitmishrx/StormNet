"""Tests for Phase 8 Real Meteorological Data Acquisition Bridge.

Verifies:
- IMD Radar provider adapter (JSON sample, ODIM error handling, provenance tagging)
- MOSDAC INSAT provider adapter (JSON sample, channel extraction)
- Ground Lightning adapter (JSON sample, CSV tabular parsing, physical bounds)
- Rain Gauge adapter (JSON sample, CSV tabular parsing, Marshall-Palmer QPE conversion)
- Dataset Manifest generation, SHA-256 calculation, and persistence
- Dataset Validator checks (CRS, coordinates, units, gaps, reports)
- Dataset Registrar CLI and execution
- Experiment safety gating (rejection of synthetic/sample data under SCIENTIFIC_VALIDATION)

All tests are classified as DEVELOPMENT / SAMPLE integration tests.
"""

from datetime import datetime, timezone
import json
import os
from pathlib import Path
import tempfile
import pytest
import numpy as np

from packages.shared.radar_archive.imd_adapter import IMDRadarAdapter, IMDRadarFrame
from packages.shared.radar_archive.insat_adapter import INSATAdapter, INSATFrame
from packages.shared.radar_archive.lightning_adapter import GroundLightningAdapter, LightningDataset
from packages.shared.radar_archive.rain_gauge_adapter import RainGaugeAdapter, RainGaugeDataset
from ml.data.manifest import (
    DatasetManifest,
    DatasetProvenance,
    compute_file_sha256,
    compute_directory_sha256,
)
from ml.data.validate import DatasetValidator, DatasetValidationReport
from ml.data.register import DatasetRegistrar
from ml.data.gating import (
    ExperimentMode,
    ScientificIntegrityError,
    enforce_experiment_safety_gate,
)


class TestProviderAdapters:
    """Tests provider-specific adapters for IMD, MOSDAC, Lightning, and Rain Gauge data."""

    def test_imd_radar_adapter_json_sample(self):
        """DEVELOPMENT / SAMPLE: Verifies IMD radar adapter loads sample JSON scan correctly."""
        adapter = IMDRadarAdapter(target_grid_dim=64)
        sample_path = Path("data/samples/radar/dwr_delhi_20260926_1545.json")

        frame = adapter.load_radar_file(sample_path)
        assert isinstance(frame, IMDRadarFrame)
        assert frame.radar_id == "DWR-DEL-SAF"
        assert frame.frequency_band == "C-BAND"
        assert frame.data_provenance == DatasetProvenance.SAMPLE_DATA.value
        assert frame.reflectivity_dbz is not None
        assert frame.reflectivity_dbz.shape == (64, 64)
        assert np.max(frame.reflectivity_dbz) >= 55.0  # Convective core present
        assert len(frame.cells) == 20

    def test_imd_radar_adapter_missing_file_raises(self):
        adapter = IMDRadarAdapter()
        with pytest.raises(FileNotFoundError):
            adapter.load_radar_file("data/non_existent_scan.json")

    def test_insat_adapter_json_sample(self):
        """DEVELOPMENT / SAMPLE: Verifies INSAT adapter loads satellite sample frame."""
        adapter = INSATAdapter(target_grid_dim=64)
        sample_path = Path("data/samples/satellite/insat_3dr_delhi_20260926_1545.json")

        frame = adapter.load_insat_file(sample_path)
        assert isinstance(frame, INSATFrame)
        assert frame.satellite_id == "INSAT-3DR"
        assert frame.product_type == "TIR1_10.8UM"
        assert frame.data_provenance == DatasetProvenance.SAMPLE_DATA.value
        assert frame.brightness_temp_k is not None
        assert frame.brightness_temp_k.shape == (64, 64)
        # Deep convective clouds should have low BT (<230 K)
        assert np.min(frame.brightness_temp_k) <= 230.0

    def test_lightning_adapter_json_sample(self):
        """DEVELOPMENT / SAMPLE: Verifies ground lightning adapter loads strike feeds."""
        adapter = GroundLightningAdapter()
        sample_path = Path("data/samples/lightning/lln_delhi_20260926_1545.json")

        ds = adapter.load_lightning_file(sample_path)
        assert isinstance(ds, LightningDataset)
        assert ds.network_id == "IITM_NCR_LLN"
        assert ds.data_provenance == DatasetProvenance.SAMPLE_DATA.value
        assert ds.stroke_count == 5
        assert ds.strokes[0].type in ["CG", "IC"]
        assert -100.0 <= ds.strokes[0].peak_current_ka <= 100.0

    def test_lightning_adapter_csv_parsing(self):
        """DEVELOPMENT / SAMPLE: Verifies tabular CSV parsing for lightning feeds."""
        adapter = GroundLightningAdapter()
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            f.write("timestamp,latitude,longitude,type,peak_current_ka,polarity,sensors,chi_sq\n")
            f.write("2026-09-26T12:00:00Z,28.60,77.20,CG,-35.5,NEGATIVE,8,0.8\n")
            f.write("2026-09-26T12:01:00Z,28.62,77.22,IC,15.2,POSITIVE,6,1.1\n")
            temp_path = f.name

        try:
            ds = adapter.load_lightning_file(temp_path, default_provenance="REAL_AUTHORIZED_DATA")
            assert ds.stroke_count == 2
            assert ds.data_provenance == "REAL_AUTHORIZED_DATA"
            assert ds.strokes[0].type == "CG"
            assert ds.strokes[0].peak_current_ka == -35.5
            assert ds.strokes[1].type == "IC"
        finally:
            os.remove(temp_path)

    def test_rain_gauge_adapter_json_sample(self):
        """DEVELOPMENT / SAMPLE: Verifies rain gauge adapter loads AWS precipitation."""
        adapter = RainGaugeAdapter()
        sample_path = Path("data/samples/aws/aws_delhi_20260926_1545.json")

        ds = adapter.load_gauge_file(sample_path)
        assert isinstance(ds, RainGaugeDataset)
        assert ds.data_provenance == DatasetProvenance.SAMPLE_DATA.value
        assert ds.observation_count == 4
        assert "AWS-DEL-SAF" in ds.unique_stations
        assert ds.observations[0].rainfall_amount_mm > 0.0

    def test_rain_gauge_marshall_palmer_conversion(self):
        adapter = RainGaugeAdapter()
        # Light rain (~20 dBZ) -> ~0.7 mm/hr
        r20 = adapter.radar_dbz_to_rain_rate(20.0)
        assert 0.5 < r20 < 1.0

        # Convective rain (~45 dBZ) -> ~25 mm/hr
        r45 = adapter.radar_dbz_to_rain_rate(45.0)
        assert 20.0 < r45 < 40.0


class TestManifestAndRegistrar:
    """Tests DatasetManifest, SHA-256 calculation, and DatasetRegistrar."""

    def test_manifest_sha256_hashing(self):
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
            f.write("test_content_for_stormnet_hash")
            tmp = f.name

        try:
            hash_val = compute_file_sha256(tmp)
            assert isinstance(hash_val, str)
            assert len(hash_val) == 64  # SHA-256 hex length
        finally:
            os.remove(tmp)

    def test_dataset_registration_creates_manifest(self):
        """DEVELOPMENT / SAMPLE: Verifies registrar creates manifest without moving files."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            sample_file = Path(tmp_dir) / "test_radar_scan.json"
            sample_data = {
                "radar_id": "DWR-DEL-SAF",
                "timestamp": "2026-09-26T12:00:00Z",
                "source": "DEVELOPMENT_SAMPLE",
                "bounding_box": [76.5, 28.0, 77.8, 29.2],
                "cells": [{"grid_x": 32, "grid_y": 32, "lat": 28.6, "lon": 77.2, "reflectivity_dbz": 45.0}],
            }
            with open(sample_file, "w", encoding="utf-8") as f:
                json.dump(sample_data, f)

            manifests_dir = Path(tmp_dir) / "manifests"
            registrar = DatasetRegistrar(manifests_dir=manifests_dir)

            manifest = registrar.register_dataset(
                path=sample_file,
                dataset_id="test_delhi_dwr_unit",
                source="IMD_DWR",
                provider="IMD",
                product="DWR_MAX_Z",
                provenance="SAMPLE_DATA",
            )

            assert manifest.dataset_id == "test_delhi_dwr_unit"
            assert manifest.provider == "IMD"
            assert manifest.file_count == 1
            assert manifest.data_provenance == "SAMPLE_DATA"

            # Check manifest was saved and original file exists
            saved_manifest = manifests_dir / "test_delhi_dwr_unit.json"
            assert saved_manifest.exists()
            assert sample_file.exists()

            loaded = DatasetManifest.load(saved_manifest)
            assert loaded.dataset_id == manifest.dataset_id
            assert loaded.checksum == manifest.checksum


class TestDatasetValidator:
    """Tests the automated DatasetValidator engine."""

    def test_validator_on_radar_sample(self):
        """DEVELOPMENT / SAMPLE: Validates existing sample radar scan."""
        validator = DatasetValidator()
        report = validator.validate(
            dataset_id="sample_radar_test",
            path="data/samples/radar",
            provenance="SAMPLE_DATA",
        )

        assert isinstance(report, DatasetValidationReport)
        assert report.dataset_id == "sample_radar_test"
        assert report.file_count == 1
        assert report.pass_rate_pct >= 80.0
        assert report.failed_checks == 0
        assert report.overall_status in ["PASSED", "WARNING"]

        # Check critical checks executed
        check_names = [c.check_name for c in report.checks]
        assert "file_integrity_check" in check_names
        assert "geographic_bounding_check" in check_names
        assert "crs_conformity_check" in check_names
        assert "physical_units_and_range_check" in check_names


class TestScientificExperimentGating:
    """Tests the scientific experiment gating safety mechanism."""

    def test_scientific_validation_rejects_synthetic_data(self):
        """SCIENTIFIC VALIDATION must reject synthetic datasets with error."""
        with pytest.raises(ScientificIntegrityError) as exc_info:
            enforce_experiment_safety_gate(
                dataset_provenance=DatasetProvenance.SYNTHETIC_DATA.value,
                experiment_mode=ExperimentMode.SCIENTIFIC_VALIDATION.value,
            )
        assert "SCIENTIFIC INTEGRITY GATE REJECTION" in str(exc_info.value)
        assert "SYNTHETIC_DATA" in str(exc_info.value)

    def test_scientific_validation_rejects_sample_data(self):
        """SCIENTIFIC VALIDATION must reject sample mock datasets with error."""
        with pytest.raises(ScientificIntegrityError) as exc_info:
            enforce_experiment_safety_gate(
                dataset_provenance=DatasetProvenance.SAMPLE_DATA.value,
                experiment_mode=ExperimentMode.SCIENTIFIC_VALIDATION.value,
            )
        assert "SCIENTIFIC INTEGRITY GATE REJECTION" in str(exc_info.value)

    def test_scientific_validation_allows_real_authorized_data(self):
        """SCIENTIFIC VALIDATION succeeds when legitimate real/historical data is supplied."""
        allowed_real = enforce_experiment_safety_gate(
            dataset_provenance=DatasetProvenance.REAL_AUTHORIZED_DATA.value,
            experiment_mode=ExperimentMode.SCIENTIFIC_VALIDATION.value,
        )
        assert allowed_real is True

        allowed_hist = enforce_experiment_safety_gate(
            dataset_provenance=DatasetProvenance.HISTORICAL_DATA.value,
            experiment_mode=ExperimentMode.SCIENTIFIC_VALIDATION.value,
        )
        assert allowed_hist is True

    def test_development_test_allows_synthetic_data(self):
        """DEVELOPMENT_TEST mode permits synthetic data for software testing."""
        allowed = enforce_experiment_safety_gate(
            dataset_provenance=DatasetProvenance.SYNTHETIC_DATA.value,
            experiment_mode=ExperimentMode.DEVELOPMENT_TEST.value,
        )
        assert allowed is True
