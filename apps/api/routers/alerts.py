"""Router for CAP-compliant emergency meteorological warnings."""

from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from apps.api.core.database import get_db
from apps.api.repositories.alert_repository import AlertRepository
from apps.api.services.alert_service import AlertService
from apps.api.schemas.alert import AlertSchema, AlertFilterParams

router = APIRouter(prefix="/alerts", tags=["Emergency Warnings (CAP)"])


def get_alert_service(db: Session = Depends(get_db)) -> AlertService:
    """Dependency provider injecting AlertRepository into AlertService."""
    repo = AlertRepository(db)
    return AlertService(repo)


@router.get("", response_model=List[AlertSchema], summary="List active emergency weather alerts")
def get_alerts(
    severity: Optional[str] = Query(None, description="Filter by IMD warning severity (YELLOW, ORANGE, RED)"),
    state: Optional[str] = Query(None, description="Filter by state name"),
    active_only: bool = Query(True, description="Only return non-expired alerts"),
    service: AlertService = Depends(get_alert_service),
) -> List[AlertSchema]:
    """Retrieves active Common Alerting Protocol (CAP) warnings dispatched for civil disaster management."""
    filters = AlertFilterParams(severity=severity, state=state, active_only=active_only)
    return service.list_alerts(filters)
