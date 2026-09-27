"""Radar Data Validation Engine for STORMNET.

Enforces physical meteorological bounds, spatial limits, timestamp sanity,
and data corruption checks before radar data enters the pipeline.
"""

from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Tuple
import numpy as np


class RadarValidationError(Exception):
    """Base exception for radar validation failures."""
    pass


class CorruptedDataError(RadarValidationError):
    """Raised when data has excessive NaNs, invalid dimensions, or unreadable blocks."""
    pass


class InvalidCoordinateError(RadarValidationError):
    """Raised when geographic bounds or antenna locations are out of physical ranges."""
    pass


class RadarValidator:
    """Validates raw and preprocessed radar payloads."""

    MIN_VALID_DBZ = -30.0
    MAX_VALID_DBZ = 85.0
    MAX_NAN_RATIO = 0.85  # Maximum allowable corrupted / NaN fraction

    @staticmethod
    def validate_timestamp(ts: datetime, max_future_minutes: int = 10, is_sample: bool = False) -> None:
        """Validates observation timestamp sanity."""
        if not isinstance(ts, datetime):
            raise RadarValidationError(f"Invalid timestamp type: {type(ts)}. Expected datetime.")

        now_utc = datetime.now(timezone.utc)
        # Normalize comparison to timezone-aware UTC
        if ts.tzinfo is None:
            ts_cmp = ts.replace(tzinfo=timezone.utc)
        else:
            ts_cmp = ts.astimezone(timezone.utc)

        if not is_sample and ts_cmp > now_utc + timedelta(minutes=max_future_minutes):
            raise RadarValidationError(
                f"Timestamp {ts.isoformat()} is in the future (> {max_future_minutes}m ahead of UTC)."
            )

        if ts_cmp < now_utc - timedelta(days=3650):  # 10 years historical ceiling
            raise RadarValidationError(f"Timestamp {ts.isoformat()} exceeds historical archival horizon.")

    @staticmethod
    def validate_coordinates(lat: float, lon: float, height_m: float = 0.0) -> None:
        """Validates antenna or observation coordinate bounds."""
        if not (-90.0 <= lat <= 90.0):
            raise InvalidCoordinateError(f"Latitude {lat} is outside valid physical range [-90, 90].")
        if not (-180.0 <= lon <= 180.0):
            raise InvalidCoordinateError(f"Longitude {lon} is outside valid physical range [-180, 180].")
        if height_m < -400.0 or height_m > 9000.0:
            raise InvalidCoordinateError(f"Elevation {height_m}m is outside terrestrial bounds.")

    @staticmethod
    def validate_bounding_box(bbox: Tuple[float, float, float, float]) -> None:
        """Validates bounding box (min_lon, min_lat, max_lon, max_lat)."""
        if len(bbox) != 4:
            raise InvalidCoordinateError(f"Bounding box must contain 4 elements (min_lon, min_lat, max_lon, max_lat). Got {bbox}.")
        min_lon, min_lat, max_lon, max_lat = bbox

        if min_lat >= max_lat:
            raise InvalidCoordinateError(f"Invalid latitude bounds: min_lat ({min_lat}) >= max_lat ({max_lat}).")
        if min_lon >= max_lon:
            raise InvalidCoordinateError(f"Invalid longitude bounds: min_lon ({min_lon}) >= max_lon ({max_lon}).")

        RadarValidator.validate_coordinates(min_lat, min_lon)
        RadarValidator.validate_coordinates(max_lat, max_lon)

    @classmethod
    def validate_reflectivity_grid(cls, grid: np.ndarray) -> Dict[str, Any]:
        """Validates Cartesian reflectivity matrix and computes health diagnostics."""
        if not isinstance(grid, np.ndarray):
            raise CorruptedDataError(f"Reflectivity grid must be a numpy.ndarray. Got {type(grid)}.")

        if grid.ndim != 2:
            raise CorruptedDataError(f"Expected 2D reflectivity grid. Got shape {grid.shape}.")

        if grid.size == 0:
            raise CorruptedDataError("Reflectivity grid is empty (size 0).")

        total_cells = grid.size
        nan_count = int(np.isnan(grid).sum())
        nan_ratio = nan_count / total_cells

        if nan_ratio > cls.MAX_NAN_RATIO:
            raise CorruptedDataError(
                f"Data quarantine triggered: NaN ratio ({nan_ratio:.2%}) exceeds threshold ({cls.MAX_NAN_RATIO:.0%})."
            )

        # Check physical ranges of non-NaN values
        valid_vals = grid[~np.isnan(grid)]
        if valid_vals.size > 0:
            min_val = float(np.min(valid_vals))
            max_val = float(np.max(valid_vals))

            if min_val < cls.MIN_VALID_DBZ or max_val > cls.MAX_VALID_DBZ:
                raise RadarValidationError(
                    f"Reflectivity values [{min_val:.1f}, {max_val:.1f}] dBZ exceed physical limits "
                    f"[{cls.MIN_VALID_DBZ}, {cls.MAX_VALID_DBZ}] dBZ."
                )

        return {
            "total_cells": total_cells,
            "nan_cells": nan_count,
            "valid_cells": int(total_cells - nan_count),
            "nan_ratio": round(nan_ratio, 4),
            "min_dbz": round(float(np.min(valid_vals)), 2) if valid_vals.size > 0 else 0.0,
            "max_dbz": round(float(np.max(valid_vals)), 2) if valid_vals.size > 0 else 0.0,
            "mean_dbz": round(float(np.mean(valid_vals)), 2) if valid_vals.size > 0 else 0.0,
        }
