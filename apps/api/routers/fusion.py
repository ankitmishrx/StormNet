"""FastAPI Router for Multi-Source Meteorological Data Fusion."""

from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from apps.api.core.database import get_db
from apps.api.services.fusion_service import FusionService
from apps.api.schemas.fusion import (
    FusedFrameDetailResponse,
    FusedGridCellHistoryResponse,
    FusionNetworkStatusResponse,
    DataSourceStatusDTO,
)

router = APIRouter(prefix="/fusion", tags=["Multi-Source Data Fusion"])


@router.get("/latest", response_model=FusedFrameDetailResponse, summary="Get latest fused meteorological frame")
def get_latest_fused_frame(
    sector_id: str = Query("delhi-ncr", description="Sector identifier"),
    db: Session = Depends(get_db),
):
    """Retrieves the latest spatio-temporally aligned composite frame combining Radar, Satellite, Lightning, and AWS."""
    service = FusionService(db)
    return service.get_latest_frame(sector_id=sector_id)


@router.get("/status", response_model=FusionNetworkStatusResponse, summary="Get fusion network health & completeness")
def get_fusion_network_status(
    sector_id: str = Query("delhi-ncr", description="Sector identifier"),
    db: Session = Depends(get_db),
):
    """Returns multi-sensor availability flags, stream latencies, and data completeness metric."""
    service = FusionService(db)
    return service.get_network_status(sector_id=sector_id)


@router.get("/sources", response_model=List[DataSourceStatusDTO], summary="List registered data sources & diagnostics")
def get_fusion_sources_status(
    db: Session = Depends(get_db),
):
    """Enumerates all registered meteorological data source adapters and health statuses."""
    service = FusionService(db)
    return service.get_sources_status()


@router.get("/grid/{grid_id}", response_model=FusedGridCellHistoryResponse, summary="Get fused feature history for a grid cell")
def get_grid_cell_feature_history(
    grid_id: str,
    limit: int = Query(12, ge=1, le=100, description="Max historical frames"),
    db: Session = Depends(get_db),
):
    """Retrieves time-series multi-sensor feature values for an individual 1–3 km grid cell."""
    service = FusionService(db)
    return service.get_grid_cell_history(grid_id=grid_id, limit=limit)


@router.get("/{timestamp}", response_model=FusedFrameDetailResponse, summary="Get fused frame by timestamp")
def get_fused_frame_by_timestamp(
    timestamp: str,
    sector_id: str = Query("delhi-ncr", description="Sector identifier"),
    db: Session = Depends(get_db),
):
    """Retrieves a historical or replay fused frame closest to the specified ISO timestamp."""
    try:
        ts = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid timestamp format '{timestamp}'. Use ISO-8601 format (e.g. 2026-09-26T15:45:00Z).",
        )

    service = FusionService(db)
    frame = service.get_frame_by_timestamp(target_time=ts, sector_id=sector_id)
    if not frame:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No fused frame found for timestamp {timestamp}",
        )
    return frame
