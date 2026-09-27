"""Repository for database operations on convective storms."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from apps.api.models.storm import Storm
from apps.api.models.storm_track import StormTrack
from apps.api.schemas.storm import StormFilterParams


class StormRepository:
    """Encapsulates spatial and relational queries for convective storm cells."""

    def __init__(self, db: Optional[Session] = None):
        self.db = db

    def get_all(self, filters: Optional[StormFilterParams] = None, limit: int = 50, offset: int = 0) -> List[Storm]:
        """Retrieves filtered list of storm cells."""
        if not self.db:
            return []
        try:
            query = self.db.query(Storm)
            if filters:
                if filters.status:
                    query = query.filter(Storm.status == filters.status)
                if filters.min_severity:
                    query = query.filter(Storm.severity_level == filters.min_severity)
                if filters.min_dbz:
                    query = query.filter(Storm.max_reflectivity_dbz >= filters.min_dbz)
            return query.order_by(Storm.max_reflectivity_dbz.desc()).offset(offset).limit(limit).all()
        except Exception:
            return []

    def get_by_id(self, storm_id: UUID) -> Optional[Storm]:
        """Fetches a single storm cell by unique UUID."""
        if not self.db:
            return None
        try:
            return self.db.query(Storm).filter(Storm.id == storm_id).first()
        except Exception:
            return None

    def get_by_code(self, cell_code: str) -> Optional[Storm]:
        """Fetches a storm by its operational code."""
        if not self.db:
            return None
        try:
            return self.db.query(Storm).filter(Storm.cell_code == cell_code).first()
        except Exception:
            return None

    def get_tracks_for_storm(self, storm_id: UUID) -> List[StormTrack]:
        """Fetches all historical and predicted track nodes for a cell."""
        if not self.db:
            return []
        try:
            return (
                self.db.query(StormTrack)
                .filter(StormTrack.storm_id == storm_id)
                .order_by(StormTrack.lead_time_minutes.asc())
                .all()
            )
        except Exception:
            return []
