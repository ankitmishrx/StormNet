"""STORMNET Isolated Demo / Simulation Replay Router.

Provides a strictly isolated demonstration pathway using development samples or synthetic simulations.
Guarantees that demo data CANNOT be accidentally presented as real operational observations.
"""

from datetime import datetime, timezone
from typing import Dict, Any, List
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from ml.data.manifest import DatasetProvenance

router = APIRouter(prefix="/demo", tags=["Demo & Simulation Replay Mode"])


class DemoStatusResponse(BaseModel):
    mode: str = Field("DEMO_REPLAY", description="Operational execution mode")
    is_operational: bool = Field(False, description="Strictly False for demo pathways")
    data_provenance: str = Field(DatasetProvenance.SAMPLE_DATA.value, description="Data provenance tag")
    active_scenario: str = Field("NCR_CONVECTIVE_EPISODE_04", description="Name of demo storm scenario")
    disclaimer: str = Field(
        "DEMO MODE ONLY: This sequence contains calibrated developmental sample or synthetic simulation data. "
        "It MUST NOT be cited or presented as live operational IMD/MoES meteorological observations.",
        description="Mandatory scientific non-operational notice",
    )
    supported_scenarios: List[Dict[str, str]] = Field(default_factory=list)


@router.get(
    "/status",
    response_model=DemoStatusResponse,
    summary="Get demo mode status and isolation parameters",
    status_code=status.HTTP_200_OK,
)
def get_demo_status() -> DemoStatusResponse:
    """Returns current demo mode configuration and non-operational disclosure."""
    return DemoStatusResponse(
        mode="DEMO_REPLAY",
        is_operational=False,
        data_provenance=DatasetProvenance.SAMPLE_DATA.value,
        active_scenario="NCR_CONVECTIVE_EPISODE_04",
        supported_scenarios=[
            {"id": "NCR_CONVECTIVE_EPISODE_04", "type": "SYNTHETIC_DATA", "description": "Rapid moving multicell convective storm"},
            {"id": "DELHI_DWR_SAMPLE_SCAN", "type": "SAMPLE_DATA", "description": "Single-frame calibrated sample radar volume"},
            {"id": "delhi-squall-sim", "type": "SYNTHETIC_DATA", "description": "Simulated Delhi squall line"},
        ],
    )


VALID_SCENARIOS = {
    "NCR_CONVECTIVE_EPISODE_04",
    "DELHI_DWR_SAMPLE_SCAN",
    "delhi-squall-sim",
}


@router.get(
    "/scenario/{scenario_id}",
    summary="Retrieve isolated demo simulation scenario",
    status_code=status.HTTP_200_OK,
)
def get_demo_scenario(scenario_id: str) -> Dict[str, Any]:
    """Provides playback frames for a demo scenario, with explicit non-operational stamps on every frame."""
    if scenario_id not in VALID_SCENARIOS:
        raise HTTPException(status_code=404, detail=f"Demo scenario '{scenario_id}' not found.")
    return {
        "scenario_id": scenario_id,
        "is_operational": False,
        "data_provenance": DatasetProvenance.SYNTHETIC_DATA.value if ("EPISODE" in scenario_id or "sim" in scenario_id.lower()) else DatasetProvenance.SAMPLE_DATA.value,
        "watermark": "DEMONSTRATION ONLY — NOT OPERATIONAL OBSERVATIONS",
        "frames": [
            {
                "step": 0,
                "lead_time_minutes": 0,
                "domain_max_dbz": 58.4,
                "provenance": DatasetProvenance.SYNTHETIC_DATA.value,
                "is_demo": True,
            },
            {
                "step": 1,
                "lead_time_minutes": 15,
                "domain_max_dbz": 54.2,
                "provenance": DatasetProvenance.SYNTHETIC_DATA.value,
                "is_demo": True,
            },
            {
                "step": 2,
                "lead_time_minutes": 30,
                "domain_max_dbz": 48.0,
                "provenance": DatasetProvenance.SYNTHETIC_DATA.value,
                "is_demo": True,
            },
        ],
    }
