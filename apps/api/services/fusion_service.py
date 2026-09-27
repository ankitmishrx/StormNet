"""Application Service for Multi-Source Meteorological Data Fusion."""

from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session

from apps.api.repositories.fusion_repository import FusionRepository
from apps.api.schemas.fusion import (
    FusedFrameDetailResponse,
    FusedGridCellHistoryResponse,
    FusionNetworkStatusResponse,
    DataSourceStatusDTO,
)


class FusionService:
    """Coordinates multi-source meteorological fusion retrieval and status diagnostics."""

    def __init__(self, db: Optional[Session]):
        self.repository = FusionRepository(db)

    def get_latest_frame(self, sector_id: str = "delhi-ncr") -> FusedFrameDetailResponse:
        """Retrieves the most recent spatio-temporally aligned fused frame."""
        return self.repository.get_latest_frame(sector_id=sector_id)

    def get_frame_by_timestamp(
        self, target_time: datetime, sector_id: str = "delhi-ncr"
    ) -> Optional[FusedFrameDetailResponse]:
        """Retrieves fused frame closest to target timestamp."""
        return self.repository.get_frame_by_timestamp(target_time=target_time, sector_id=sector_id)

    def get_grid_cell_history(
        self, grid_id: str, limit: int = 12
    ) -> FusedGridCellHistoryResponse:
        """Retrieves chronological feature history for an individual grid cell."""
        return self.repository.get_grid_cell_history(grid_id=grid_id, limit=limit)

    def get_network_status(self, sector_id: str = "delhi-ncr") -> FusionNetworkStatusResponse:
        """Returns aggregate network health and completeness score."""
        return self.repository.get_network_status(sector_id=sector_id)

    def get_sources_status(self) -> List[DataSourceStatusDTO]:
        """Returns individual stream telemetry statuses."""
        return self.repository.get_sources_status()
