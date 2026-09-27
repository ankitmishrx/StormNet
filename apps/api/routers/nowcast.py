"""FastAPI Router for Spatiotemporal U-Net Convective Nowcasting."""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status

from apps.api.schemas.nowcast import (
    NowcastPredictRequest,
    NowcastResponse,
)
from apps.api.services.nowcast_inference_service import NowcastInferenceService

router = APIRouter(prefix="/nowcast", tags=["Convective Nowcasting Engine"])

# Shared singleton service instance
_nowcast_service = NowcastInferenceService()


def get_nowcast_service() -> NowcastInferenceService:
    return _nowcast_service


@router.post(
    "/predict",
    response_model=NowcastResponse,
    summary="Trigger convective nowcast prediction",
    status_code=status.HTTP_200_OK,
)
def predict_nowcast(
    request: NowcastPredictRequest,
    service: NowcastInferenceService = Depends(get_nowcast_service),
) -> NowcastResponse:
    """Executes Spatiotemporal U-Net forward pass for short-term convective extrapolation."""
    return service.predict(request)


@router.get(
    "/latest",
    response_model=NowcastResponse,
    summary="Get latest convective nowcast forecast",
    status_code=status.HTTP_200_OK,
)
def get_latest_nowcast(
    sector_id: str = Query("delhi-ncr", description="Sector identifier"),
    service: NowcastInferenceService = Depends(get_nowcast_service),
) -> NowcastResponse:
    """Retrieves the most recent nowcast prediction sequence with data source provenance."""
    return service.get_run("latest")


@router.get(
    "/{run_id}",
    response_model=NowcastResponse,
    summary="Get nowcast prediction run by ID",
    status_code=status.HTTP_200_OK,
)
def get_nowcast_by_id(
    run_id: str,
    service: NowcastInferenceService = Depends(get_nowcast_service),
) -> NowcastResponse:
    """Retrieves an archived nowcasting prediction run by its unique run identifier."""
    result = service.get_run(run_id)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Nowcast run '{run_id}' not found.")
    return result
