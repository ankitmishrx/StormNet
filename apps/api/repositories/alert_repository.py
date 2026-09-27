"""Repository for CAP alerts and emergency warnings."""

from typing import List, Optional
from datetime import datetime
from uuid import UUID
from sqlalchemy.orm import Session
from apps.api.models.alert import Alert
from apps.api.schemas.alert import AlertFilterParams


class AlertRepository:
    """Queries for CAP warnings and disaster alerts."""

    def __init__(self, db: Optional[Session] = None):
        self.db = db

    def get_all(self, filters: Optional[AlertFilterParams] = None, limit: int = 50) -> List[Alert]:
        """Fetches active alerts matching filter criteria."""
        if not self.db:
            return []
        try:
            query = self.db.query(Alert)
            now = datetime.utcnow()
            if filters:
                if filters.active_only:
                    query = query.filter(Alert.effective_from <= now, Alert.expires_at >= now)
                if filters.severity:
                    query = query.filter(Alert.severity == filters.severity)
            return query.order_by(Alert.created_at.desc()).limit(limit).all()
        except Exception:
            return []

    def get_by_id(self, alert_id: UUID) -> Optional[Alert]:
        """Fetches a single alert by ID."""
        if not self.db:
            return None
        try:
            return self.db.query(Alert).filter(Alert.id == alert_id).first()
        except Exception:
            return None
