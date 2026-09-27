"""Radar Data Abstraction Interfaces for STORMNET.

Defines vendor-agnostic contracts for raw radar sources, polar volumes,
sweeps, Cartesian frames, and individual observations.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
import numpy as np


@dataclass
class RadarObservation:
    """Discrete single radar observation or grid-cell value."""

    latitude: float
    longitude: float
    reflectivity_dbz: float
    timestamp: datetime
    quality_flag: str = "VALID"  # VALID, CLUTTER_FILTERED, DEGRADED, NODATA
    altitude_m: Optional[float] = None
    radial_velocity_ms: Optional[float] = None


@dataclass
class RadarSweep:
    """Single elevation sweep in polar coordinates (azimuth x range)."""

    elevation_angle_deg: float
    azimuth_angles_deg: np.ndarray  # shape: (n_rays,)
    range_bins_m: np.ndarray  # shape: (n_bins,)
    reflectivity: np.ndarray  # shape: (n_rays, n_bins)
    doppler_velocity: Optional[np.ndarray] = None
    spectrum_width: Optional[np.ndarray] = None
    quality_flags: Optional[np.ndarray] = None


@dataclass
class RadarVolume:
    """3D polar volume scan composed of multiple elevation sweeps."""

    radar_id: str
    station_name: str
    antenna_lat: float
    antenna_lon: float
    antenna_height_m: float
    frequency_band: str  # C-BAND, S-BAND, X-BAND
    timestamp: datetime
    sweeps: List[RadarSweep] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RadarFrame:
    """Decoded 2D Cartesian radar product (e.g. Composite Reflectivity Z_comp)."""

    frame_id: str
    radar_id: str
    source: str  # DEVELOPMENT_SAMPLE, IMD_DWR_LOCAL, OPERA_HDF5
    timestamp: datetime
    product_type: str  # COMPOSITE_REFLECTIVITY, CAPPI_2KM, SURFACE_RAIN_RATE
    crs: str  # EPSG:4326
    bounding_box: Tuple[float, float, float, float]  # (min_lon, min_lat, max_lon, max_lat)
    source_resolution_km: float
    target_grid_km: float
    grid_matrix: np.ndarray  # 2D array of dBZ values
    lats: np.ndarray  # 1D latitude coordinates
    lons: np.ndarray  # 1D longitude coordinates
    max_dbz: float
    min_dbz: float
    mean_dbz: float
    quality_status: str  # VALIDATED, DEGRADED, SAMPLE
    total_valid_cells: int
    metadata: Dict[str, Any] = field(default_factory=dict)


class RadarDataSource(ABC):
    """Abstract generic radar data source adapter."""

    @abstractmethod
    def read_volume(self, file_path: str) -> RadarVolume:
        """Reads raw radar file and returns parsed RadarVolume."""
        pass

    @abstractmethod
    def read_cappi(self, file_path: str, altitude_km: float = 2.0) -> RadarFrame:
        """Reads or derives Cartesian CAPPI product from radar dataset."""
        pass

    @abstractmethod
    def read_composite_reflectivity(self, file_path: str) -> RadarFrame:
        """Extracts column-maximum composite reflectivity from radar dataset."""
        pass
