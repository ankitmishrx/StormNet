"""Preprocessing pipeline for radar volume sweeps and Cartesian CAPPI gridding."""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
import numpy as np


class BaseRadarPreprocessor(ABC):
    """Abstract interface for radar quality control, decluttering, and gridding."""

    @abstractmethod
    def remove_ground_clutter(self, raw_reflectivity: np.ndarray) -> np.ndarray:
        """Applies dual-polarization and Doppler velocity filters to remove non-meteorological echoes."""
        pass

    @abstractmethod
    def interpolate_cappi(
        self,
        polar_volume: np.ndarray,
        elevation_angles: list[float],
        target_altitude_km: float,
    ) -> np.ndarray:
        """Interpolates polar radar sweeps onto a standard Cartesian grid at a constant altitude."""
        pass

    @abstractmethod
    def compute_composite_reflectivity(self, volume_cappi: np.ndarray) -> np.ndarray:
        """Computes column-maximum composite reflectivity (Z_comp) across all vertical levels."""
        pass


class StandardRadarPreprocessor(BaseRadarPreprocessor):
    """Default implementation for standard Cartesian radar preprocessing."""

    def remove_ground_clutter(self, raw_reflectivity: np.ndarray) -> np.ndarray:
        # Standard thresholding: mask values below 10 dBZ and non-meteorological noise
        cleaned = np.copy(raw_reflectivity)
        cleaned[cleaned < 10.0] = 0.0
        return cleaned

    def interpolate_cappi(
        self,
        polar_volume: np.ndarray,
        elevation_angles: list[float],
        target_altitude_km: float,
    ) -> np.ndarray:
        # Placeholder for 3D Barnes or Nearest-Neighbor Cartesian gridding
        return np.squeeze(polar_volume) if polar_volume.ndim > 2 else polar_volume

    def compute_composite_reflectivity(self, volume_cappi: np.ndarray) -> np.ndarray:
        if volume_cappi.ndim == 3:
            return np.max(volume_cappi, axis=0)
        return volume_cappi
