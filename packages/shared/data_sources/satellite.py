"""INSAT Geostationary Satellite data source interface and adapters."""

from datetime import datetime
from typing import Any, List, Optional
from pydantic import BaseModel
from packages.shared.data_sources.base import (
    BaseDataSource,
    DataSourceHealth,
    DataSourceHealthStatus,
    DataSourceType,
    IngestionResult,
)


class SatelliteChannelMetadata(BaseModel):
    """Metadata for geostationary satellite spectral channels."""
    satellite_name: str  # e.g., INSAT-3D, INSAT-3DR
    channel_name: str  # TIR-1, TIR-2, MIR, WV, VIS
    central_wavelength_um: float
    spatial_resolution_km: float


class INSATPayload(BaseModel):
    """Container for INSAT Rapid Scan georeferenced raster."""
    satellite_name: str
    scan_timestamp: datetime
    is_rapid_scan: bool
    channels: List[SatelliteChannelMetadata]
    extent_bbox: List[float]
    storage_uri: Optional[str] = None


class BaseSatelliteDataSource(BaseDataSource[INSATPayload]):
    """Abstract interface for satellite radiance data providers."""

    def __init__(self, provider_name: str = "ISRO-MOSDAC-INSAT"):
        super().__init__(provider_name=provider_name, source_type=DataSourceType.SATELLITE_INSAT)


class MockSatelliteAdapter(BaseSatelliteDataSource):
    """Development satellite adapter. Clearly labeled as non-operational mock."""

    async def check_health(self) -> DataSourceHealth:
        return DataSourceHealth(
            source_type=self.source_type,
            provider_name=self.provider_name,
            status=DataSourceHealthStatus.ONLINE,
            last_received_at=datetime.utcnow(),
            latency_seconds=310.0,
            message="INSAT-3DR Rapid Scan active in development mode",
        )

    async def fetch_latest(self) -> IngestionResult[INSATPayload]:
        now = datetime.utcnow()
        payload = INSATPayload(
            satellite_name="INSAT-3DR",
            scan_timestamp=now,
            is_rapid_scan=True,
            channels=[
                SatelliteChannelMetadata(
                    satellite_name="INSAT-3DR",
                    channel_name="TIR-1",
                    central_wavelength_um=10.8,
                    spatial_resolution_km=4.0,
                ),
                SatelliteChannelMetadata(
                    satellite_name="INSAT-3DR",
                    channel_name="WV",
                    central_wavelength_um=6.8,
                    spatial_resolution_km=8.0,
                ),
            ],
            extent_bbox=[65.0, 5.0, 98.0, 38.0],
            storage_uri="/data/samples/insat_sample.h5",
        )
        return IngestionResult(
            success=True,
            source_type=self.source_type,
            timestamp=now,
            record_count=1,
            data=payload,
            metadata={"adapter_mode": "DEVELOPMENT_STUB"},
        )

    def validate_payload(self, raw_data: Any) -> bool:
        return raw_data is not None
