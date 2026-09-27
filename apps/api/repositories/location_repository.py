"""Repository for geographic and administrative locations."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from apps.api.models.location import Location
from apps.api.schemas.location import LocationFilterParams


class LocationRepository:
    """Queries for locations, districts, and strategic nodes."""

    def __init__(self, db: Optional[Session] = None):
        self.db = db

    def get_all(self, filters: Optional[LocationFilterParams] = None, limit: int = 100) -> List[Location]:
        """Fetches locations matching filter criteria."""
        if not self.db:
            return []
        try:
            query = self.db.query(Location)
            if filters:
                if filters.state:
                    query = query.filter(Location.state == filters.state)
                if filters.district:
                    query = query.filter(Location.district == filters.district)
                if filters.location_type:
                    query = query.filter(Location.location_type == filters.location_type)
            return query.order_by(Location.name.asc()).limit(limit).all()
        except Exception:
            return []

    def get_by_id(self, location_id: UUID) -> Optional[Location]:
        """Fetches a location by ID."""
        if not self.db:
            return None
        try:
            return self.db.query(Location).filter(Location.id == location_id).first()
        except Exception:
            return None
