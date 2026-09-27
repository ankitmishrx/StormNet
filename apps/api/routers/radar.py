"""FastAPI Router for Doppler Weather Radar operations."""

import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from apps.api.core.database import get_db
from apps.api.services.radar_service import RadarService
from apps.api.schemas.radar import (
    RadarFrameSummary,
    RadarFrameDetail,
    RadarGridResponse,
    RadarStatusResponse,
)

router = APIRouter(prefix="/radar", tags=["Doppler Weather Radar (DWR)"])


@router.get("/latest", response_model=RadarFrameDetail, summary="Get latest processed radar frame")
def get_latest_radar_frame(
    sector_id: str = Query("delhi-ncr", description="Sector identifier (e.g. delhi-ncr)"),
    db: Session = Depends(get_db),
):
    """Retrieves the most recent radar observation frame including summary statistics and vector contours."""
    service = RadarService(db)
    return service.get_latest_frame(sector_id=sector_id)


@router.get("/frames", response_model=List[RadarFrameSummary], summary="List radar observation frames")
def list_radar_frames(
    limit: int = Query(10, ge=1, le=100, description="Max records to return"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    db: Session = Depends(get_db),
):
    """Lists chronological radar frames available in the system."""
    service = RadarService(db)
    return service.list_frames(limit=limit, offset=offset)


@router.get("/status", response_model=RadarStatusResponse, summary="Get radar network health & data freshness")
def get_radar_network_status(
    radar_id: str = Query("DWR-DEL-SAF", description="Radar Station Identifier"),
    db: Session = Depends(get_db),
):
    """Returns operational status, latency, and data freshness tier (LIVE, HISTORICAL, SAMPLE, STALE)."""
    service = RadarService(db)
    return service.get_radar_status(radar_id=radar_id)


@router.get("/{frame_id}", response_model=RadarFrameDetail, summary="Get radar frame by ID")
def get_radar_frame_by_id(
    frame_id: uuid.UUID,
    db: Session = Depends(get_db),
):
    """Retrieves detailed metadata for a specific radar observation frame."""
    service = RadarService(db)
    frame = service.get_frame_by_id(frame_id)
    if not frame:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Radar frame {frame_id} not found")
    return frame


@router.get("/{frame_id}/grid", response_model=RadarGridResponse, summary="Get gridded radar observations")
def get_radar_frame_grid(
    frame_id: uuid.UUID,
    db: Session = Depends(get_db),
):
    """Returns gridded reflectivity observations (1–3 km resolution) for the specified frame."""
    service = RadarService(db)
    return service.get_frame_grid(frame_id)
