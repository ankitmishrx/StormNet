"""STORMNET Repositories Registry."""

from apps.api.repositories.storm_repository import StormRepository
from apps.api.repositories.forecast_repository import ForecastRepository
from apps.api.repositories.hazard_repository import HazardRepository
from apps.api.repositories.alert_repository import AlertRepository
from apps.api.repositories.location_repository import LocationRepository

__all__ = [
    "StormRepository",
    "ForecastRepository",
    "HazardRepository",
    "AlertRepository",
    "LocationRepository",
]
