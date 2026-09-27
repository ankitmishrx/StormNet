"""Pydantic schemas for geographic and administrative locations."""

from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, Field


class LocationSchema(BaseModel):
    """Geographic location reference."""
    id: UUID
    name: str
    location_type: str
    state: str
    district: Optional[str] = None
    elevation_m: Optional[float] = None
    population: Optional[int] = None
    coordinates: List[float] = Field(..., description="[longitude, latitude]")


class LocationFilterParams(BaseModel):
    """Filter parameters for location queries."""
    state: Optional[str] = None
    district: Optional[str] = None
    location_type: Optional[str] = None
