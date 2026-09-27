"""Router for convective storms and cell tracking endpoints."""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from apps.api.core.database import get_db
from apps.api.repositories.storm_repository import StormRepository
from apps.api.services.storm_service import StormService
from apps.api.schemas.storm import (
    StormSummarySchema,
    StormDetailSchema,
    StormFilterParams,
)

router = APIRouter(prefix="/storms", tags=["Convective Storms"])


def get_storm_service(db: Session = Depends(get_db)) -> StormService:
    """Dependency provider injecting StormRepository into StormService."""
    repo = StormRepository(db)
    return StormService(repo)


@router.get("", response_model=List[StormSummarySchema], summary="List active convective storm cells")
def get_storms(
    status: Optional[str] = Query("ACTIVE", description="Cell status (ACTIVE, DISSIPATING, ALL)"),
    min_severity: Optional[str] = Query(None, description="Minimum IMD warning level (YELLOW, ORANGE, RED)"),
    min_dbz: Optional[float] = Query(None, description="Minimum reflectivity threshold in dBZ"),
    service: StormService = Depends(get_storm_service),
) -> List[StormSummarySchema]:
    """Retrieves all active convective cells tracked in the operational radar composite."""
    filters = StormFilterParams(status=status, min_severity=min_severity, min_dbz=min_dbz)
    return service.list_storms(filters)


@router.get("/{storm_id}", response_model=StormDetailSchema, summary="Get storm cell diagnostics and track")
def get_storm_by_id(
    storm_id: UUID,
    service: StormService = Depends(get_storm_service),
) -> StormDetailSchema:
    """Retrieves physical diagnostics (VIL, Echo Top) and 0-60m projected motion vectors for a cell."""
    return service.get_storm_detail(storm_id)
