"""Archive-Level Quality Control (QC) Pipeline for multi-station radar datasets."""

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Any
import numpy as np

from packages.shared.radar_archive.adapter import ArchiveFrameRecord
from packages.shared.radar_archive.stations import RadarStation, get_station_registry


@dataclass
class QualityControlReport:
    """Standardized audit report of archive-level quality metrics."""
    station_id: str
    total_files_scanned: int
    valid_frames_count: int
    corrupted_files_count: int
    duplicate_timestamps_count: int
    invalid_timestamps_count: int
    temporal_gaps_count: int
    longest_gap_hours: float
    expected_cadence_minutes: float
    pass_rate_percentage: float
    flagged_issues: List[Dict[str, Any]] = field(default_factory=list)
    generated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    @property
    def is_acceptable_for_training(self) -> bool:
        """Determines if the archive meets minimum scientific thresholds for ML."""
        return self.valid_frames_count >= 10 and self.pass_rate_percentage >= 80.0


class ArchiveQualityController:
    """Enforces rigorous meteorological data quality standards across historical archives."""

    def __init__(
        self,
        expected_cadence_minutes: float = 10.0,
        max_allowable_gap_minutes: float = 20.0,
        min_valid_dbz: float = -30.0,
        max_valid_dbz: float = 80.0,
    ):
        self.expected_cadence = expected_cadence_minutes
        self.max_gap_minutes = max_allowable_gap_minutes
        self.min_valid_dbz = min_valid_dbz
        self.max_valid_dbz = max_valid_dbz
        self.registry = get_station_registry()

    def run_qc_audit(
        self,
        station_id: str,
        records: List[ArchiveFrameRecord],
    ) -> QualityControlReport:
        """Runs a complete QC evaluation over an indexed sequence of radar frames."""
        total = len(records)
        if total == 0:
            return QualityControlReport(
                station_id=station_id,
                total_files_scanned=0,
                valid_frames_count=0,
                corrupted_files_count=0,
                duplicate_timestamps_count=0,
                invalid_timestamps_count=0,
                temporal_gaps_count=0,
                longest_gap_hours=0.0,
                expected_cadence_minutes=self.expected_cadence,
                pass_rate_percentage=0.0,
                flagged_issues=[{"severity": "ERROR", "message": "No files found in archive"}],
            )

        corrupt_count = sum(1 for r in records if r.qc_status == "CORRUPT")
        duplicate_count = sum(1 for r in records if r.qc_status == "DUPLICATE")
        invalid_ts_count = sum(1 for r in records if r.qc_status == "INVALID_TIMESTAMP")
        valid_records = [r for r in records if r.is_valid]

        issues: List[Dict[str, Any]] = []

        # Analyze temporal continuity among valid chronological frames
        temporal_gaps = 0
        longest_gap_sec = 0.0

        for i in range(1, len(valid_records)):
            delta = (valid_records[i].timestamp - valid_records[i - 1].timestamp).total_seconds()
            gap_min = delta / 60.0

            if delta > longest_gap_sec:
                longest_gap_sec = delta

            if gap_min > self.max_gap_minutes:
                temporal_gaps += 1
                issues.append({
                    "severity": "WARNING",
                    "type": "TEMPORAL_GAP",
                    "from_ts": valid_records[i - 1].timestamp.isoformat(),
                    "to_ts": valid_records[i].timestamp.isoformat(),
                    "gap_duration_minutes": round(gap_min, 1),
                })

        longest_gap_hours = round(longest_gap_sec / 3600.0, 2)
        valid_count = len(valid_records)
        pass_rate = round((valid_count / total) * 100.0, 2)

        return QualityControlReport(
            station_id=station_id,
            total_files_scanned=total,
            valid_frames_count=valid_count,
            corrupted_files_count=corrupt_count,
            duplicate_timestamps_count=duplicate_count,
            invalid_timestamps_count=invalid_ts_count,
            temporal_gaps_count=temporal_gaps,
            longest_gap_hours=longest_gap_hours,
            expected_cadence_minutes=self.expected_cadence,
            pass_rate_percentage=pass_rate,
            flagged_issues=issues,
        )

    def validate_grid_array(
        self,
        grid_array: np.ndarray,
        expected_shape: tuple[int, int] = (64, 64),
    ) -> Dict[str, Any]:
        """Validates numerical integrity of a decoded 2D reflectivity grid."""
        errors: List[str] = []

        if grid_array.shape != expected_shape:
            errors.append(f"Unexpected shape: {grid_array.shape}, expected {expected_shape}")

        if np.isnan(grid_array).any():
            errors.append("Grid contains NaN values")

        if np.isinf(grid_array).any():
            errors.append("Grid contains Infinite values")

        min_val = float(np.min(grid_array))
        max_val = float(np.max(grid_array))

        if min_val < self.min_valid_dbz or max_val > self.max_valid_dbz:
            errors.append(f"Reflectivity range [{min_val}, {max_val}] dBZ exceeds valid limits [{self.min_valid_dbz}, {self.max_valid_dbz}] dBZ")

        return {
            "is_valid": len(errors) == 0,
            "min_dbz": min_val,
            "max_dbz": max_val,
            "errors": errors,
        }
