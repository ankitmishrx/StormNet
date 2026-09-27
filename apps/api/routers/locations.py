"""Router for geographical locations and meteorological stations."""

from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from apps.api.core.database import get_db
from apps.api.repositories.location_repository import LocationRepository
from apps.api.services.location_service import LocationService
from apps.api.schemas.location import LocationSchema, LocationFilterParams

router = APIRouter(prefix="/locations", tags=["Geographic Locations"])


def get_location_service(db: Session = Depends(get_db)) -> LocationService:
    """Dependency provider injecting LocationRepository into LocationService."""
    repo = LocationRepository(db)
    return LocationService(repo)


@router.get("", response_model=List[LocationSchema], summary="List reference sites and administrative points")
def get_locations(
    state: Optional[str] = Query(None, description="Filter by state name"),
    district: Optional[str] = Query(None, description="Filter by district name"),
    location_type: Optional[str] = Query(None, description="Type (RADAR_SITE, AIRPORT, AWS_STATION, DISTRICT)"),
    service: LocationService = Depends(get_location_service),
) -> List[LocationSchema]:
    """Returns strategic geographic reference points in the domain."""
    filters = LocationFilterParams(state=state, district=district, location_type=location_type)
    return service.list_locations(filters)
