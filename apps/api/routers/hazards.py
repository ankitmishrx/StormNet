"""Router for convective hazard probabilities (Cloudburst, Hail, Squall, Lightning)."""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from apps.api.core.database import get_db
from apps.api.repositories.hazard_repository import HazardRepository
from apps.api.services.hazard_service import HazardService
from apps.api.schemas.hazard import (
    HazardCardSchema,
    HazardPredictionDetailSchema,
)

router = APIRouter(prefix="/hazards", tags=["Convective Hazards"])


def get_hazard_service(db: Session = Depends(get_db)) -> HazardService:
    """Dependency provider injecting HazardRepository into HazardService."""
    repo = HazardRepository(db)
    return HazardService(repo)


@router.get("", response_model=List[HazardCardSchema], summary="Get hazard probability cards (Research Prototype)")
def get_hazards(
    storm_id: Optional[UUID] = Query(None, description="Optional cell ID to filter hazards for a specific cell"),
    service: HazardService = Depends(get_hazard_service),
) -> List[HazardCardSchema]:
    """Returns hazard probability cards for cloudburst, hail, squall winds, and lightning."""
    return service.get_hazard_cards_for_cell(storm_id)


@router.get("/cell/{storm_id}", response_model=HazardPredictionDetailSchema, summary="Get full hazard prediction for cell")
def get_cell_hazard_prediction(
    storm_id: UUID,
    service: HazardService = Depends(get_hazard_service),
) -> HazardPredictionDetailSchema:
    """Retrieves detailed probabilistic hazard telemetry for a given convective storm cell."""
    return service.get_cell_hazard_detail(storm_id)
