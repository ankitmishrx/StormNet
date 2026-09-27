"""Convective feature engineering pipeline for thermodynamic and kinematic metrics."""

from abc import ABC, abstractmethod
from typing import Dict, Any
import numpy as np


class FeaturePipeline(ABC):
    """Abstract interface for extracting physical convective features from radar grids."""

    @abstractmethod
    def extract_features(self, radar_volume: np.ndarray, metadata: Dict[str, Any]) -> Dict[str, np.ndarray]:
        """Extracts Vertically Integrated Liquid (VIL), Echo Tops, and growth rate fields."""
        pass


class ConvectiveFeatureExtractor(FeaturePipeline):
    """Extracts Vertically Integrated Liquid (VIL) and Echo Tops (18 dBZ boundary)."""

    def __init__(self, z_threshold_dbz: float = 18.0):
        self.z_threshold_dbz = z_threshold_dbz

    def calculate_vil(self, volume_reflectivity_dbz: np.ndarray, delta_z_km: float = 1.0) -> np.ndarray:
        """Calculates Vertically Integrated Liquid (kg/m^2) using standard Z-M relation: M = 3.44e-3 * Z^(4/7)."""
        if volume_reflectivity_dbz.ndim < 3:
            return np.zeros_like(volume_reflectivity_dbz)

        # Convert dBZ to linear reflectivity factor Z (mm^6/m^3)
        z_linear = 10.0 ** (volume_reflectivity_dbz / 10.0)
        # Liquid water content M (g/m^3)
        lwc = 3.44e-3 * (z_linear ** (4.0 / 7.0))
        # Integrate vertically: VIL = sum(lwc * dz) * 1e-3 (kg/m^2)
        vil = np.sum(lwc, axis=0) * delta_z_km * 1e-3
        return vil

    def calculate_echo_tops(
        self, volume_reflectivity_dbz: np.ndarray, vertical_levels_km: list[float]
    ) -> np.ndarray:
        """Calculates height of the 18 dBZ echo boundary (km MSL)."""
        if volume_reflectivity_dbz.ndim < 3:
            return np.zeros_like(volume_reflectivity_dbz)

        mask = volume_reflectivity_dbz >= self.z_threshold_dbz
        echo_tops = np.zeros(volume_reflectivity_dbz.shape[1:], dtype=float)

        for i, alt in enumerate(vertical_levels_km):
            echo_tops[mask[i]] = alt

        return echo_tops

    def extract_features(self, radar_volume: np.ndarray, metadata: Dict[str, Any]) -> Dict[str, np.ndarray]:
        vertical_levels = metadata.get("vertical_levels_km", [1.0, 2.0, 3.0, 4.0, 6.0, 8.0, 10.0, 12.0, 14.0])
        vil = self.calculate_vil(radar_volume)
        echo_tops = self.calculate_echo_tops(radar_volume, vertical_levels)
        z_comp = np.max(radar_volume, axis=0) if radar_volume.ndim == 3 else radar_volume

        return {
            "composite_reflectivity": z_comp,
            "vertically_integrated_liquid": vil,
            "echo_top_height": echo_tops,
        }
