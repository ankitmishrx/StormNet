"""STORMNET Schemas Registry."""

from apps.api.schemas.common import (
    PointGeometry,
    PolygonGeometry,
    LineStringGeometry,
    GeoJSONFeature,
    GeoJSONFeatureCollection,
    PaginatedResponse,
    HealthResponse,
)
from apps.api.schemas.storm import (
    StormBaseSchema,
    StormSummarySchema,
    StormDetailSchema,
    StormTrackPointSchema,
    StormFilterParams,
)
from apps.api.schemas.forecast import (
    ForecastFrameSchema,
    ForecastTimelineResponse,
)
from apps.api.schemas.hazard import (
    HazardCardSchema,
    HazardPredictionDetailSchema,
)
from apps.api.schemas.alert import (
    AlertSchema,
    AlertFilterParams,
)
from apps.api.schemas.location import (
    LocationSchema,
    LocationFilterParams,
)

__all__ = [
    "PointGeometry",
    "PolygonGeometry",
    "LineStringGeometry",
    "GeoJSONFeature",
    "GeoJSONFeatureCollection",
    "PaginatedResponse",
    "HealthResponse",
    "StormBaseSchema",
    "StormSummarySchema",
    "StormDetailSchema",
    "StormTrackPointSchema",
    "StormFilterParams",
    "ForecastFrameSchema",
    "ForecastTimelineResponse",
    "HazardCardSchema",
    "HazardPredictionDetailSchema",
    "AlertSchema",
    "AlertFilterParams",
    "LocationSchema",
    "LocationFilterParams",
]
