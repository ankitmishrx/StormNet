"""Base abstractions and contract interfaces for meteorological data sources."""

from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Generic, List, Optional, TypeVar
from pydantic import BaseModel, Field

T = TypeVar("T")


class DataSourceType(str, Enum):
    """Categorical classification of meteorological observation streams."""
    RADAR_DWR = "RADAR_DWR"
    SATELLITE_INSAT = "SATELLITE_INSAT"
    LIGHTNING_LLN = "LIGHTNING_LLN"
    SURFACE_AWS = "SURFACE_AWS"


class DataSourceHealthStatus(str, Enum):
    """Operational health status of an external data ingestion stream."""
    ONLINE = "ONLINE"
    DEGRADED = "DEGRADED"
    OFFLINE = "OFFLINE"
    MAINTENANCE = "MAINTENANCE"


class DataSourceHealth(BaseModel):
    """Health diagnostic payload for an active data source."""
    source_type: DataSourceType
    provider_name: str
    status: DataSourceHealthStatus
    last_received_at: Optional[datetime] = None
    latency_seconds: Optional[float] = None
    message: str = "Operating nominally"


class IngestionResult(BaseModel, Generic[T]):
    """Standard container returned by data source adapters."""
    success: bool
    source_type: DataSourceType
    timestamp: datetime
    record_count: int
    data: Optional[T] = None
    errors: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class BaseDataSource(ABC, Generic[T]):
    """Abstract interface defining required contract methods for meteorological providers."""

    def __init__(self, provider_name: str, source_type: DataSourceType):
        self.provider_name = provider_name
        self.source_type = source_type

    @abstractmethod
    async def check_health(self) -> DataSourceHealth:
        """Polls provider endpoint and returns operational connection status."""
        pass

    @abstractmethod
    async def fetch_latest(self) -> IngestionResult[T]:
        """Ingests the most recently available volume scan, satellite frame, or sensor batch."""
        pass

    @abstractmethod
    def validate_payload(self, raw_data: Any) -> bool:
        """Validates payload schema, bounding box coordinates, and numeric range integrity."""
        pass
