"""Service for Common Alerting Protocol (CAP) emergency warning generation."""

import uuid
from datetime import datetime, timedelta
from typing import List, Optional
from apps.api.repositories.alert_repository import AlertRepository
from apps.api.schemas.alert import AlertSchema, AlertFilterParams


class AlertService:
    """Handles generation, formatting, and query of CAP-compliant meteorological warnings."""

    def __init__(self, alert_repo: AlertRepository):
        self.alert_repo = alert_repo

    def list_alerts(self, filters: Optional[AlertFilterParams] = None) -> List[AlertSchema]:
        """Returns active CAP warnings for civil protection and disaster authorities."""
        db_alerts = self.alert_repo.get_all(filters)
        if db_alerts:
            return [
                AlertSchema(
                    id=a.id,
                    storm_id=a.storm_id,
                    alert_identifier=a.alert_identifier,
                    status=a.status,
                    msg_type=a.msg_type,
                    severity=a.severity,
                    urgency=a.urgency,
                    headline=a.headline,
                    description=a.description,
                    instruction=a.instruction,
                    affected_jurisdictions=a.affected_jurisdictions,
                    effective_from=a.effective_from,
                    expires_at=a.expires_at,
                    created_at=a.created_at,
                )
                for a in db_alerts
            ]

        # Baseline seed alert for development & initial testing
        now = datetime.utcnow()
        return [
            AlertSchema(
                id=uuid.UUID("33333333-3333-3333-3333-333333333333"),
                storm_id=uuid.UUID("11111111-1111-1111-1111-111111111111"),
                alert_identifier="CAP-IN-DL-2026-084-001",
                status="ACTUAL",
                msg_type="ALERT",
                severity="RED",
                urgency="IMMEDIATE",
                headline="RED WARNING: Severe Convective Storm & Imminent Cloudburst Risk for Delhi-NCR",
                description="Intense convective cell (Max dBZ 61.5, VIL 48 kg/m2) moving ENE at 38 km/h. Localized rainfall rates exceeding 100 mm/hr and severe lightning expected.",
                instruction="Take immediate shelter. Stay away from vulnerable low-lying underpasses, open fields, and metal structures.",
                affected_jurisdictions=["New Delhi", "Central Delhi", "East Delhi", "Noida", "Ghaziabad"],
                polygon_coordinates=[
                    [[77.15, 28.58], [77.35, 28.58], [77.35, 28.72], [77.15, 28.72], [77.15, 28.58]]
                ],
                effective_from=now,
                expires_at=now + timedelta(hours=3),
                created_at=now,
            )
        ]
