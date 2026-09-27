"""STORMNET Database Models Registry."""

from apps.api.models.storm import Storm
from apps.api.models.storm_track import StormTrack
from apps.api.models.observation import Observation
from apps.api.models.grid_cell import GridCell
from apps.api.models.forecast import Forecast
from apps.api.models.hazard_prediction import HazardPrediction
from apps.api.models.alert import Alert
from apps.api.models.location import Location
from apps.api.models.model_run import ModelRun
from apps.api.models.radar_frame import RadarFrameModel
from apps.api.models.radar_observation import RadarObservationModel
from apps.api.models.radar_product import RadarProductModel
from apps.api.models.fused_grid_frame import FusedGridFrameModel
from apps.api.models.fused_grid_feature import FusedGridFeatureModel
from apps.api.models.data_source_status import DataSourceStatusModel

__all__ = [
    "Storm",
    "StormTrack",
    "Observation",
    "GridCell",
    "Forecast",
    "HazardPrediction",
    "Alert",
    "Location",
    "ModelRun",
    "RadarFrameModel",
    "RadarObservationModel",
    "RadarProductModel",
    "FusedGridFrameModel",
    "FusedGridFeatureModel",
    "DataSourceStatusModel",
]

