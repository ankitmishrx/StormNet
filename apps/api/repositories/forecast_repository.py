"""Repository for convective nowcast timeline frames."""

from typing import List, Optional
from datetime import datetime
from uuid import UUID
from sqlalchemy.orm import Session
from apps.api.models.forecast import Forecast


class ForecastRepository:
    """Handles temporal and spatial queries for nowcasting frames."""

    def __init__(self, db: Optional[Session] = None):
        self.db = db

    def get_timeline(self, sector_id: str, base_time: Optional[datetime] = None) -> List[Forecast]:
        """Fetches 0-6 hour forecast frames for a sector."""
        if not self.db:
            return []
        try:
            query = self.db.query(Forecast).filter(Forecast.sector_id == sector_id)
            if base_time:
                query = query.filter(Forecast.base_time == base_time)
            return query.order_by(Forecast.lead_time_minutes.asc()).all()
        except Exception:
            return []

    def get_by_id(self, forecast_id: UUID) -> Optional[Forecast]:
        """Fetches a specific nowcast frame by ID."""
        if not self.db:
            return None
        try:
            return self.db.query(Forecast).filter(Forecast.id == forecast_id).first()
        except Exception:
            return None
