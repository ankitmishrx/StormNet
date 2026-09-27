"""Router for 0-6 hour convective nowcasting timeline endpoints."""

from typing import Optional
from datetime import datetime
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from apps.api.core.database import get_db
from apps.api.repositories.forecast_repository import ForecastRepository
from apps.api.services.forecast_service import ForecastService
from apps.api.schemas.forecast import ForecastTimelineResponse

router = APIRouter(prefix="/forecasts", tags=["Nowcasting Forecasts"])


def get_forecast_service(db: Session = Depends(get_db)) -> ForecastService:
    """Dependency provider injecting ForecastRepository into ForecastService."""
    repo = ForecastRepository(db)
    return ForecastService(repo)


@router.get("", response_model=ForecastTimelineResponse, summary="Get 0-6 hour nowcast timeline steps")
def get_forecast_timeline(
    sector_id: str = Query("delhi-ncr", description="Operational sector identifier"),
    base_time: Optional[datetime] = Query(None, description="Observation anchor time T-0 (ISO UTC)"),
    service: ForecastService = Depends(get_forecast_service),
) -> ForecastTimelineResponse:
    """Returns 0-6 hour discrete nowcast steps, lead-time confidence index, and tile reference paths."""
    return service.get_timeline(sector_id, base_time)
