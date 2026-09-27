"""Pydantic schemas for Common Alerting Protocol (CAP) emergency warnings."""

from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID
from pydantic import BaseModel


class AlertSchema(BaseModel):
    """CAP-compliant emergency alert summary."""
    id: UUID
    storm_id: Optional[UUID] = None
    alert_identifier: str
    status: str
    msg_type: str
    severity: str
    urgency: str
    headline: str
    description: str
    instruction: Optional[str] = None
    affected_jurisdictions: Optional[List[str]] = None
    polygon_coordinates: Optional[List[List[List[float]]]] = None
    effective_from: datetime
    expires_at: datetime
    created_at: datetime


class AlertFilterParams(BaseModel):
    """Filter parameters for alert queries."""
    severity: Optional[str] = None
    state: Optional[str] = None
    active_only: bool = True
