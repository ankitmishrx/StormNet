"""Core interfaces, contracts, and quality flag enumerations for Multi-Source Data Fusion."""

from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple
from pydantic import BaseModel, Field
import uuid


class QualityFlag(str, Enum):
    """Unified data quality classification for meteorological observations."""
    VALID = "VALID"
    MISSING = "MISSING"
    INVALID = "INVALID"
    STALE = "STALE"
    LOW_QUALITY = "LOW_QUALITY"
    UNAVAILABLE = "UNAVAILABLE"


class DataFreshnessTier(str, Enum):
    """Categorical freshness tier for incoming sensor telemetry."""
    LIVE = "LIVE"
    HISTORICAL = "HISTORICAL"
    REPLAY = "REPLAY"
    SAMPLE = "SAMPLE"
    STALE = "STALE"
    UNAVAILABLE = "UNAVAILABLE"


class TemporalWindow(BaseModel):
    """Defines a discrete temporal observation synchronization window."""
    window_start: datetime
    window_end: datetime
    anchor_timestamp: datetime
    duration_seconds: int = 300  # Default 5-minute window


class MeteorologicalObservation(BaseModel):
    """Normalized observation contract for any physical meteorological sensor."""
    source_name: str
    sensor_id: str
    timestamp: datetime
    latitude: float
    longitude: float
    variable_name: str
    value: Optional[float] = None
    unit: str
    quality_flag: QualityFlag = QualityFlag.VALID
    source_resolution_km: Optional[float] = None
    geometry: Optional[Dict[str, Any]] = None  # GeoJSON representation
    metadata: Dict[str, Any] = Field(default_factory=dict)


class SatelliteObservation(BaseModel):
    """Observation frame from geostationary meteorological satellite (e.g. INSAT-3DR)."""
    satellite_id: str
    timestamp: datetime
    channel: str = "TIR1_10.8UM"
    latitude: float
    longitude: float
    brightness_temp_kelvin: Optional[float] = None
    cloud_top_temp_kelvin: Optional[float] = None
    cooling_rate_kelvin_per_hour: Optional[float] = None
    quality_flag: QualityFlag = QualityFlag.VALID
    source_resolution_km: float = 4.0
    metadata: Dict[str, Any] = Field(default_factory=dict)


class LightningObservation(BaseModel):
    """Single lightning strike or flash detected by a lightning location network."""
    event_id: str
    network_id: str = "IITM_LLN"
    timestamp: datetime
    latitude: float
    longitude: float
    strike_type: str = "CG"  # CG = Cloud-to-Ground, IC = Intra-Cloud
    peak_current_ka: Optional[float] = None
    polarity: str = "NEGATIVE"  # POSITIVE or NEGATIVE
    quality_flag: QualityFlag = QualityFlag.VALID
    metadata: Dict[str, Any] = Field(default_factory=dict)


class AtmosphericObservation(BaseModel):
    """In-situ surface automatic weather station (AWS) observation."""
    station_id: str
    timestamp: datetime
    latitude: float
    longitude: float
    temperature_celsius: Optional[float] = None
    relative_humidity_pct: Optional[float] = None
    pressure_hpa: Optional[float] = None
    wind_speed_kmh: Optional[float] = None
    wind_direction_deg: Optional[float] = None
    precipitation_rate_mmh: Optional[float] = None
    quality_flag: QualityFlag = QualityFlag.VALID
    metadata: Dict[str, Any] = Field(default_factory=dict)


class FusedGridCellFeature(BaseModel):
    """Unified multi-sensor feature representation binned onto a 1–3 km grid cell."""
    grid_id: str
    timestamp: datetime
    latitude: float
    longitude: float
    grid_size_km: float = 3.0

    # Radar variables
    radar_reflectivity_dbz: Optional[float] = None
    radar_max_dbz: Optional[float] = None
    radar_precip_rate_mm_hr: Optional[float] = None
    radar_quality: QualityFlag = QualityFlag.MISSING

    # Satellite variables
    satellite_brightness_temp_k: Optional[float] = None
    satellite_cloud_cooling_rate_k_hr: Optional[float] = None
    satellite_quality: QualityFlag = QualityFlag.MISSING

    # Lightning variables
    lightning_strike_count: int = 0
    lightning_density_per_km2: float = 0.0
    lightning_rate_per_min: float = 0.0
    lightning_trend: str = "STABLE"  # STABLE, INCREASING, DECREASING
    lightning_quality: QualityFlag = QualityFlag.MISSING

    # Atmospheric / Surface AWS variables
    atmospheric_temp_c: Optional[float] = None
    atmospheric_humidity_pct: Optional[float] = None
    atmospheric_pressure_hpa: Optional[float] = None
    atmospheric_wind_speed_kmh: Optional[float] = None
    atmospheric_quality: QualityFlag = QualityFlag.MISSING

    # Composite cell quality flag
    composite_quality: QualityFlag = QualityFlag.VALID


class FusedGridFrame(BaseModel):
    """Spatio-temporally aligned multi-source observation frame for a sector."""
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    sector_id: str = "delhi-ncr"
    timestamp: datetime
    window_start: datetime
    window_end: datetime
    resolution_km: float = 3.0
    bounding_box: List[float] = Field(default_factory=lambda: [76.5, 28.0, 77.8, 29.2])
    data_freshness: DataFreshnessTier = DataFreshnessTier.SAMPLE

    # Source availability tracking
    radar_available: bool = False
    satellite_available: bool = False
    lightning_available: bool = False
    atmospheric_available: bool = False
    completeness_score: float = 0.0

    # Grid cell payload
    cells_count: int = 0
    cells: List[FusedGridCellFeature] = Field(default_factory=list)
    lineage_metadata: Dict[str, Any] = Field(default_factory=dict)


class BaseMeteorologicalAdapter(ABC):
    """Abstract interface for modality-specific meteorological ingest adapters."""

    @abstractmethod
    def load_from_file(self, file_path: str) -> List[Any]:
        """Loads and parses raw modality file into normalized observation list."""
        pass

    @abstractmethod
    def validate_observations(self, observations: List[Any]) -> List[Any]:
        """Validates observations against physical bounds and temporal constraints."""
        pass
