"""Doppler Weather Radar (DWR) data source interface and adapters."""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel
from packages.shared.data_sources.base import (
    BaseDataSource,
    DataSourceHealth,
    DataSourceHealthStatus,
    DataSourceType,
    IngestionResult,
)


class DWRVolumeScanMetadata(BaseModel):
    """Metadata describing a multi-elevation radar volume scan."""
    station_code: str  # e.g., DWR-DEL-SAF
    station_name: str
    latitude: float
    longitude: float
    altitude_m: float
    scan_start_utc: datetime
    scan_end_utc: datetime
    elevation_angles_deg: List[float]
    max_range_km: float
    range_resolution_m: float
    polarization: str = "DUAL_POL"  # DUAL_POL, SINGLE_POL
    variables_available: List[str] = ["DBZ", "VEL", "WIDTH", "ZDR", "KDP", "RHOHV"]


class DWRVolumeScan(BaseModel):
    """Container for processed Cartesian Constant Altitude Plan Position Indicator (CAPPI) grid."""
    metadata: DWRVolumeScanMetadata
    grid_shape: List[int]  # [altitude_levels, y_dim, x_dim]
    extent_bbox: List[float]  # [min_lon, min_lat, max_lon, max_lat]
    max_reflectivity_dbz: float
    storage_uri: Optional[str] = None


class BaseRadarDataSource(BaseDataSource[DWRVolumeScan]):
    """Abstract interface for Doppler Weather Radar data providers."""

    def __init__(self, provider_name: str = "IMD-DWR-Composite"):
        super().__init__(provider_name=provider_name, source_type=DataSourceType.RADAR_DWR)


class MockRadarAdapter(BaseRadarDataSource):
    """Development and testing radar adapter. Clearly labeled as non-operational mock."""

    def __init__(self, station_code: str = "DWR-DEL-SAF"):
        super().__init__(provider_name=f"Mock-DWR-{station_code}")
        self.station_code = station_code

    async def check_health(self) -> DataSourceHealth:
        return DataSourceHealth(
            source_type=self.source_type,
            provider_name=self.provider_name,
            status=DataSourceHealthStatus.ONLINE,
            last_received_at=datetime.utcnow(),
            latency_seconds=124.0,
            message="Mock adapter operating normally in development mode",
        )

    async def fetch_latest(self) -> IngestionResult[DWRVolumeScan]:
        now = datetime.utcnow()
        meta = DWRVolumeScanMetadata(
            station_code=self.station_code,
            station_name="IMD Safdarjung Radar",
            latitude=28.5847,
            longitude=77.2069,
            altitude_m=216.0,
            scan_start_utc=now,
            scan_end_utc=now,
            elevation_angles_deg=[0.5, 1.0, 2.0, 3.5, 5.0, 7.0, 9.5, 12.0, 15.0, 19.5],
            max_range_km=250.0,
            range_resolution_m=250.0,
        )
        scan = DWRVolumeScan(
            metadata=meta,
            grid_shape=[16, 500, 500],
            extent_bbox=[75.5, 27.0, 78.5, 30.0],
            max_reflectivity_dbz=61.5,
            storage_uri="/data/samples/radar_sample.nc",
        )
        return IngestionResult(
            success=True,
            source_type=self.source_type,
            timestamp=now,
            record_count=1,
            data=scan,
            metadata={"adapter_mode": "DEVELOPMENT_STUB"},
        )

    def validate_payload(self, raw_data: Any) -> bool:
        return raw_data is not None
