"""Service layer for Doppler Weather Radar operations."""

import uuid
from typing import List, Optional
from sqlalchemy.orm import Session

from apps.api.repositories.radar_repository import RadarRepository
from apps.api.schemas.radar import (
    RadarFrameSummary,
    RadarFrameDetail,
    RadarGridResponse,
    RadarStatusResponse,
)


class RadarService:
    """Encapsulates radar business logic and repository interactions."""

    def __init__(self, db: Session):
        self.repository = RadarRepository(db)

    def get_latest_frame(self, sector_id: str = "delhi-ncr") -> RadarFrameDetail:
        return self.repository.get_latest_frame(sector_id)

    def list_frames(self, limit: int = 10, offset: int = 0) -> List[RadarFrameSummary]:
        return self.repository.list_frames(limit=limit, offset=offset)

    def get_frame_by_id(self, frame_id: uuid.UUID) -> Optional[RadarFrameDetail]:
        return self.repository.get_frame_by_id(frame_id)

    def get_frame_grid(self, frame_id: uuid.UUID) -> RadarGridResponse:
        return self.repository.get_frame_grid(frame_id)

    def get_radar_status(self, radar_id: str = "DWR-DEL-SAF") -> RadarStatusResponse:
        return self.repository.get_radar_status(radar_id)
