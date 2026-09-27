"""Shared schemas, GeoJSON primitives, and API response wrappers."""

from typing import Generic, List, Optional, TypeVar, Any, Dict
from pydantic import BaseModel, Field

T = TypeVar("T")


class PointGeometry(BaseModel):
    """GeoJSON Point geometry representation."""
    type: str = "Point"
    coordinates: List[float] = Field(..., description="[longitude, latitude]")


class PolygonGeometry(BaseModel):
    """GeoJSON Polygon geometry representation."""
    type: str = "Polygon"
    coordinates: List[List[List[float]]] = Field(..., description="Array of linear ring coordinate arrays")


class LineStringGeometry(BaseModel):
    """GeoJSON LineString geometry representation."""
    type: str = "LineString"
    coordinates: List[List[float]] = Field(..., description="Array of coordinate points")


class GeoJSONFeature(BaseModel, Generic[T]):
    """Standard RFC 7946 GeoJSON Feature wrapper."""
    type: str = "Feature"
    geometry: Dict[str, Any]
    properties: T


class GeoJSONFeatureCollection(BaseModel, Generic[T]):
    """Standard RFC 7946 GeoJSON FeatureCollection wrapper."""
    type: str = "FeatureCollection"
    features: List[GeoJSONFeature[T]]


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated envelope for list endpoints."""
    items: List[T]
    total: int
    page: int
    page_size: int
    has_more: bool


class HealthResponse(BaseModel):
    """Health check diagnostic response."""
    status: str
    environment: str
    version: str
    timestamp: str
    services: Dict[str, str]
