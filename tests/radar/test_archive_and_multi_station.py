"""Unit and Integration Test Suite for Phase 7 Multi-Station Archive & Evaluation."""

import os
from datetime import datetime, timezone, timedelta
import numpy as np
import pytest

from packages.shared.radar_archive.stations import get_station_registry, RadarStation
from packages.shared.radar_archive.adapter import HistoricalRadarArchiveAdapter, ArchiveFrameRecord
from packages.shared.radar_archive.qc import ArchiveQualityController
from packages.shared.radar_archive.normalizer import MultiStationNormalizer
from packages.shared.radar_archive.events import ConvectiveEventExtractor, ConvectiveEventRecord
from ml.training.splitter import EventBlockedSplitter, StormEpisode
from ml.evaluation.multi_station_evaluator import MultiStationEvaluator


class TestRadarStationRegistry:
    """Verifies physical metadata registry for target Indian DWR stations."""

    def test_registered_stations_presence(self):
        registry = get_station_registry()
        station_ids = registry.list_station_ids()

        expected = ["DWR-DEL-SAF", "DWR-MUM-VER", "DWR-CHE-PRT", "DWR-KOL-SUB"]
        for st in expected:
            assert st in station_ids, f"Station {st} missing from registry"

    def test_verified_station_coordinates_and_hardware(self):
        registry = get_station_registry()
        delhi = registry.get_station("DWR-DEL-SAF")
        assert delhi is not None
        assert 28.0 <= delhi.latitude <= 29.0
        assert 77.0 <= delhi.longitude <= 78.0
        assert delhi.frequency_band == "S-Band"
        assert delhi.max_range_km == 250.0

        mumbai = registry.get_station("DWR-MUM-VER")
        assert mumbai is not None
        assert 18.5 <= mumbai.latitude <= 19.5
        assert 72.0 <= mumbai.longitude <= 73.5


class TestHistoricalArchiveAdapter:
    """Verifies file discovery, timestamp parsing, and cataloging."""

    def test_timestamp_parsing_from_filenames(self):
        adapter = HistoricalRadarArchiveAdapter()

        ts1 = adapter.parse_timestamp_from_filename("DWR_DEL_20240715_143000.h5")
        assert ts1 == datetime(2024, 7, 15, 14, 30, 0, tzinfo=timezone.utc)

        ts2 = adapter.parse_timestamp_from_filename("dwr_mumbai_20240810_0915.json")
        assert ts2 == datetime(2024, 8, 10, 9, 15, 0, tzinfo=timezone.utc)

        ts_invalid = adapter.parse_timestamp_from_filename("corrupted_radar_file.txt")
        assert ts_invalid is None

    def test_archive_record_flagging(self):
        rec_valid = ArchiveFrameRecord(
            station_id="DWR-DEL-SAF",
            timestamp=datetime(2024, 7, 15, 12, 0, tzinfo=timezone.utc),
            file_path="dummy/path.h5",
            file_format="ODIM_H5",
            product_type="MAX_Z",
            resolution_km=3.0,
            file_size_bytes=1024,
            is_valid=True,
            qc_status="VALID",
        )
        assert rec_valid.is_valid is True
        assert rec_valid.qc_status == "VALID"


class TestArchiveQualityControl:
    """Verifies QC audit rules for corrupt files, gaps, and value limits."""

    def test_qc_audit_gaps_and_pass_rate(self):
        qc = ArchiveQualityController(expected_cadence_minutes=10.0, max_allowable_gap_minutes=20.0)

        t0 = datetime(2024, 7, 15, 12, 0, tzinfo=timezone.utc)
        records = [
            ArchiveFrameRecord("DWR-DEL-SAF", t0, "f1.h5", "ODIM_H5", "MAX_Z", 3.0, 1000, True, "VALID"),
            ArchiveFrameRecord("DWR-DEL-SAF", t0 + timedelta(minutes=10), "f2.h5", "ODIM_H5", "MAX_Z", 3.0, 1000, True, "VALID"),
            # Gap of 40 minutes (> 20 min threshold)
            ArchiveFrameRecord("DWR-DEL-SAF", t0 + timedelta(minutes=50), "f3.h5", "ODIM_H5", "MAX_Z", 3.0, 1000, True, "VALID"),
            # Corrupt frame
            ArchiveFrameRecord("DWR-DEL-SAF", t0 + timedelta(minutes=60), "f4.h5", "ODIM_H5", "MAX_Z", 3.0, 0, False, "CORRUPT"),
        ]

        report = qc.run_qc_audit("DWR-DEL-SAF", records)
        assert report.total_files_scanned == 4
        assert report.valid_frames_count == 3
        assert report.corrupted_files_count == 1
        assert report.temporal_gaps_count == 1
        assert report.pass_rate_percentage == 75.0

    def test_grid_array_value_limits(self):
        qc = ArchiveQualityController()

        valid_grid = np.ones((64, 64), dtype=np.float32) * 45.0
        res_valid = qc.validate_grid_array(valid_grid)
        assert res_valid["is_valid"] is True

        out_of_bounds_grid = np.ones((64, 64), dtype=np.float32) * 120.0  # > 80 dBZ impossible
        res_invalid = qc.validate_grid_array(out_of_bounds_grid)
        assert res_invalid["is_valid"] is False


class TestMultiStationNormalizer:
    """Verifies grid normalization and spatial standardization."""

    def test_grid_normalization(self):
        normalizer = MultiStationNormalizer(target_shape=(64, 64), target_resolution_km=3.0)
        raw_grid = np.full((128, 128), 50.0, dtype=np.float32)

        vol = normalizer.normalize_grid(
            station_id="DWR-DEL-SAF",
            timestamp_utc="2026-07-04T12:00:00Z",
            raw_reflectivity_grid=raw_grid,
            source_resolution_km=0.5,
        )

        assert vol.station_id == "DWR-DEL-SAF"
        assert vol.grid_dbz.shape == (64, 64)
        assert vol.grid_resolution_km == 3.0
        assert vol.source_resolution_km == 0.5
        assert vol.crs == "EPSG:4326"
        assert vol.max_dbz == 50.0


class TestConvectiveEventExtractor:
    """Verifies event detection criteria."""

    def test_extract_convective_event(self):
        extractor = ConvectiveEventExtractor(
            convective_threshold_dbz=35.0,
            min_convective_cells=5,
            min_duration_minutes=30.0,
        )

        t0 = datetime(2026, 7, 4, 12, 0, tzinfo=timezone.utc)
        timestamps = [t0 + timedelta(minutes=i * 10) for i in range(5)]

        # Construct 5 frames with active convective core (10 cells >= 45 dBZ)
        grids = []
        for _ in range(5):
            g = np.zeros((64, 64), dtype=np.float32)
            g[20:25, 20:22] = 48.0  # 10 cells >= 35 dBZ
            grids.append(g)

        extent = {"min_lat": 27.7, "max_lat": 29.5, "min_lon": 76.2, "max_lon": 78.2}
        events = extractor.extract_events_from_grids("DWR-DEL-SAF", timestamps, grids, extent)

        assert len(events) == 1
        evt = events[0]
        assert evt.station_id == "DWR-DEL-SAF"
        assert evt.duration_minutes == 40.0
        assert evt.peak_dbz == 48.0
        assert evt.frame_count == 5


class TestMultiStationSplitterAndEvaluator:
    """Verifies leave-one-station-out cross-validation and evaluation matrix."""

    def test_leave_one_station_out_split(self):
        splitter = EventBlockedSplitter()
        episodes_by_station = {
            "DWR-DEL-SAF": [
                StormEpisode("DEL-01", datetime(2026, 7, 1, tzinfo=timezone.utc), datetime(2026, 7, 1, 6, tzinfo=timezone.utc), "DWR-DEL-SAF", sample_indices=[0, 1]),
            ],
            "DWR-MUM-VER": [
                StormEpisode("MUM-01", datetime(2026, 7, 3, tzinfo=timezone.utc), datetime(2026, 7, 3, 6, tzinfo=timezone.utc), "DWR-MUM-VER", sample_indices=[2, 3]),
            ],
            "DWR-CHE-PRT": [
                StormEpisode("CHE-01", datetime(2026, 7, 5, tzinfo=timezone.utc), datetime(2026, 7, 5, 6, tzinfo=timezone.utc), "DWR-CHE-PRT", sample_indices=[4, 5]),
            ],
        }

        # Hold out Chennai
        splits = splitter.leave_one_station_out_split(episodes_by_station, test_station_id="DWR-CHE-PRT")

        assert splits.test_indices == [4, 5]
        assert set(splits.train_indices) == {0, 1, 2, 3}
        assert len(set(splits.train_indices).intersection(set(splits.test_indices))) == 0

    def test_multi_station_evaluator_unmounted_handling(self):
        evaluator = MultiStationEvaluator()

        # Only Delhi has data; Mumbai, Chennai, Kolkata unmounted
        station_test_data = {
            "DWR-DEL-SAF": {
                "features": np.ones((2, 4, 4, 64, 64), dtype=np.float32) * 0.5,
                "targets": np.ones((2, 6, 64, 64), dtype=np.float32) * 37.5,
                "num_events": 1,
            },
            "DWR-MUM-VER": None,
            "DWR-CHE-PRT": None,
            "DWR-KOL-SUB": None,
        }

        results = evaluator.evaluate_multi_station(station_test_data)
        assert results["stations"]["DWR-DEL-SAF"]["status"] == "EVALUATED"
        assert results["stations"]["DWR-MUM-VER"]["status"] == "NOT AVAILABLE"
        assert results["stations"]["DWR-CHE-PRT"]["status"] == "NOT AVAILABLE"
        assert results["stations"]["DWR-KOL-SUB"]["status"] == "NOT AVAILABLE"
