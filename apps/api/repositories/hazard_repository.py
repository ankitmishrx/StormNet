"""Repository for hazard probability predictions."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from apps.api.models.hazard_prediction import HazardPrediction


class HazardRepository:
    """Queries for cloudburst, hail, and convective wind hazard probabilities."""

    def __init__(self, db: Optional[Session] = None):
        self.db = db

    def get_latest_for_storm(self, storm_id: UUID) -> Optional[HazardPrediction]:
        """Fetches the most recent hazard prediction for a storm cell."""
        if not self.db:
            return None
        return (
            self.db.query(HazardPrediction)
            .filter(HazardPrediction.storm_id == storm_id)
            .order_by(HazardPrediction.timestamp.desc())
            .first()
        )

    def get_high_risk_hazards(self, cloudburst_threshold: float = 0.7) -> List[HazardPrediction]:
        """Fetches all current hazards exceeding severe cloudburst probability threshold."""
        if not self.db:
            return []
        return (
            self.db.query(HazardPrediction)
            .filter(HazardPrediction.cloudburst_probability >= cloudburst_threshold)
            .order_by(HazardPrediction.cloudburst_probability.desc())
            .all()
        )
