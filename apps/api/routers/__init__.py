"""STORMNET API Routers Registry."""

from apps.api.routers.storms import router as storms_router
from apps.api.routers.forecasts import router as forecasts_router
from apps.api.routers.hazards import router as hazards_router
from apps.api.routers.alerts import router as alerts_router
from apps.api.routers.locations import router as locations_router
from apps.api.routers.radar import router as radar_router
from apps.api.routers.fusion import router as fusion_router
from apps.api.routers.nowcast import router as nowcast_router
from apps.api.routers.demo import router as demo_router
from apps.api.routers.public_data import router as public_data_router

__all__ = [
    "storms_router",
    "forecasts_router",
    "hazards_router",
    "alerts_router",
    "locations_router",
    "radar_router",
    "fusion_router",
    "nowcast_router",
    "demo_router",
    "public_data_router",
]

