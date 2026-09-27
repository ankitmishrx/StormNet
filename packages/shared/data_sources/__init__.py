"""STORMNET Data Sources Registry."""

from packages.shared.data_sources.base import (
    BaseDataSource,
    DataSourceType,
    DataSourceHealthStatus,
    DataSourceHealth,
    IngestionResult,
)
from packages.shared.data_sources.radar import (
    BaseRadarDataSource,
    DWRVolumeScan,
    DWRVolumeScanMetadata,
    MockRadarAdapter,
)
from packages.shared.data_sources.satellite import (
    BaseSatelliteDataSource,
    INSATPayload,
    SatelliteChannelMetadata,
    MockSatelliteAdapter,
)
from packages.shared.data_sources.lightning import (
    BaseLightningDataSource,
    LightningStroke,
    LightningBatch,
    MockLightningAdapter,
)
from packages.shared.data_sources.surface_obs import (
    BaseSurfaceObsDataSource,
    AWSStationReading,
    AWSNetworkBatch,
    MockSurfaceObsAdapter,
)

__all__ = [
    "BaseDataSource",
    "DataSourceType",
    "DataSourceHealthStatus",
    "DataSourceHealth",
    "IngestionResult",
    "BaseRadarDataSource",
    "DWRVolumeScan",
    "DWRVolumeScanMetadata",
    "MockRadarAdapter",
    "BaseSatelliteDataSource",
    "INSATPayload",
    "SatelliteChannelMetadata",
    "MockSatelliteAdapter",
    "BaseLightningDataSource",
    "LightningStroke",
    "LightningBatch",
    "MockLightningAdapter",
    "BaseSurfaceObsDataSource",
    "AWSStationReading",
    "AWSNetworkBatch",
    "MockSurfaceObsAdapter",
]
