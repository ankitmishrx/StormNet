"""Ground-based Lightning Location Network (LLN) data source interface and adapters."""

from datetime import datetime
from typing import Any, List
from pydantic import BaseModel
from packages.shared.data_sources.base import (
    BaseDataSource,
    DataSourceHealth,
    DataSourceHealthStatus,
    DataSourceType,
    IngestionResult,
)


class LightningStroke(BaseModel):
    """Individual detected lightning discharge."""
    stroke_id: str
    timestamp: datetime
    latitude: float
    longitude: float
    peak_current_ka: float
    stroke_type: str  # CG (Cloud-to-Ground), IC (Intra-Cloud)
    multiplicity: int = 1


class LightningBatch(BaseModel):
    """Batch of lightning strokes detected across an operational sector."""
    network_name: str  # e.g., IITM-Damini-Network, EarthNetworks
    start_time: datetime
    end_time: datetime
    total_strokes: int
    cg_strokes_count: int
    ic_strokes_count: int
    strokes: List[LightningStroke]


class BaseLightningDataSource(BaseDataSource[LightningBatch]):
    """Abstract interface for Lightning Location Network data providers."""

    def __init__(self, provider_name: str = "IITM-LLN"):
        super().__init__(provider_name=provider_name, source_type=DataSourceType.LIGHTNING_LLN)


class MockLightningAdapter(BaseLightningDataSource):
    """Development lightning adapter. Clearly labeled as non-operational mock."""

    async def check_health(self) -> DataSourceHealth:
        return DataSourceHealth(
            source_type=self.source_type,
            provider_name=self.provider_name,
            status=DataSourceHealthStatus.ONLINE,
            last_received_at=datetime.utcnow(),
            latency_seconds=12.0,
            message="LLN feed healthy in development mode",
        )

    async def fetch_latest(self) -> IngestionResult[LightningBatch]:
        now = datetime.utcnow()
        strokes = [
            LightningStroke(
                stroke_id="STRK-001",
                timestamp=now,
                latitude=28.6250,
                longitude=77.2150,
                peak_current_ka=-34.2,
                stroke_type="CG",
            ),
            LightningStroke(
                stroke_id="STRK-002",
                timestamp=now,
                latitude=28.6310,
                longitude=77.2280,
                peak_current_ka=-42.0,
                stroke_type="CG",
            ),
        ]
        batch = LightningBatch(
            network_name=self.provider_name,
            start_time=now,
            end_time=now,
            total_strokes=len(strokes),
            cg_strokes_count=2,
            ic_strokes_count=0,
            strokes=strokes,
        )
        return IngestionResult(
            success=True,
            source_type=self.source_type,
            timestamp=now,
            record_count=len(strokes),
            data=batch,
            metadata={"adapter_mode": "DEVELOPMENT_STUB"},
        )

    def validate_payload(self, raw_data: Any) -> bool:
        return raw_data is not None
