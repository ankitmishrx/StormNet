"""Radar Archive Package providing multi-station indexing, QC, normalization, and event extraction."""

from packages.shared.radar_archive.stations import (
    RadarStation,
    RadarStationRegistry,
    get_station_registry,
)
from packages.shared.radar_archive.adapter import (
    ArchiveFrameRecord,
    HistoricalRadarArchiveAdapter,
)
from packages.shared.radar_archive.qc import (
    QualityControlReport,
    ArchiveQualityController,
)
from packages.shared.radar_archive.normalizer import (
    NormalizedRadarVolume,
    MultiStationNormalizer,
)
from packages.shared.radar_archive.events import (
    ConvectiveEventRecord,
    ConvectiveEventExtractor,
)

from packages.shared.radar_archive.imd_adapter import (
    IMDRadarFrame,
    IMDRadarAdapter,
)
from packages.shared.radar_archive.insat_adapter import (
    INSATFrame,
    INSATAdapter,
)
from packages.shared.radar_archive.lightning_adapter import (
    LightningStrokeRecord,
    LightningDataset,
    GroundLightningAdapter,
)
from packages.shared.radar_archive.rain_gauge_adapter import (
    RainGaugeObservation,
    RainGaugeDataset,
    RainGaugeAdapter,
)

__all__ = [
    "RadarStation",
    "RadarStationRegistry",
    "get_station_registry",
    "ArchiveFrameRecord",
    "HistoricalRadarArchiveAdapter",
    "QualityControlReport",
    "ArchiveQualityController",
    "NormalizedRadarVolume",
    "MultiStationNormalizer",
    "ConvectiveEventRecord",
    "ConvectiveEventExtractor",
    "IMDRadarFrame",
    "IMDRadarAdapter",
    "INSATFrame",
    "INSATAdapter",
    "LightningStrokeRecord",
    "LightningDataset",
    "GroundLightningAdapter",
    "RainGaugeObservation",
    "RainGaugeDataset",
    "RainGaugeAdapter",
]
