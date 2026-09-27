"""Automatic Weather Station (AWS) surface telemetry data source interface."""

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


class AWSStationReading(BaseModel):
    """Telemetry readings from a single ground meteorological station."""
    station_id: str
    station_name: str
    timestamp: datetime
    latitude: float
    longitude: float
    elevation_m: float
    temperature_c: float
    relative_humidity_pct: float
    pressure_hpa: float
    rainfall_1h_mm: float
    rainfall_rate_mmh: float
    wind_speed_kmh: float
    wind_gust_kmh: float
    wind_direction_deg: float


class AWSNetworkBatch(BaseModel):
    """Batch of telemetry reports from a regional AWS network."""
    network_id: str  # e.g., IMD-AWS-National, State-Agriculture-AWS
    batch_timestamp: datetime
    total_reporting_stations: int
    readings: List[AWSStationReading]


class BaseSurfaceObsDataSource(BaseDataSource[AWSNetworkBatch]):
    """Abstract interface for ground-based surface observation networks."""

    def __init__(self, provider_name: str = "IMD-AWS-Composite"):
        super().__init__(provider_name=provider_name, source_type=DataSourceType.SURFACE_AWS)


class MockSurfaceObsAdapter(BaseSurfaceObsDataSource):
    """Development surface observation adapter. Clearly labeled as non-operational mock."""

    async def check_health(self) -> DataSourceHealth:
        return DataSourceHealth(
            source_type=self.source_type,
            provider_name=self.provider_name,
            status=DataSourceHealthStatus.ONLINE,
            last_received_at=datetime.utcnow(),
            latency_seconds=180.0,
            message="AWS Network 98.4% reporting in development mode",
        )

    async def fetch_latest(self) -> IngestionResult[AWSNetworkBatch]:
        now = datetime.utcnow()
        readings = [
            AWSStationReading(
                station_id="AWS-DEL-01",
                station_name="Safdarjung Base",
                timestamp=now,
                latitude=28.5847,
                longitude=77.2069,
                elevation_m=216.0,
                temperature_c=29.4,
                relative_humidity_pct=88.0,
                pressure_hpa=1004.2,
                rainfall_1h_mm=42.0,
                rainfall_rate_mmh=78.0,
                wind_speed_kmh=45.0,
                wind_gust_kmh=82.0,
                wind_direction_deg=70.0,
            )
        ]
        batch = AWSNetworkBatch(
            network_id=self.provider_name,
            batch_timestamp=now,
            total_reporting_stations=1,
            readings=readings,
        )
        return IngestionResult(
            success=True,
            source_type=self.source_type,
            timestamp=now,
            record_count=1,
            data=batch,
            metadata={"adapter_mode": "DEVELOPMENT_STUB"},
        )

    def validate_payload(self, raw_data: Any) -> bool:
        return raw_data is not None
