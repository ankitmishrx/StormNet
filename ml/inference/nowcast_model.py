"""Inference interfaces and prediction containers for 0-6 hour nowcast models."""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
import numpy as np


class PredictionResult(BaseModel):
    """Container holding forecasted spatio-temporal grids and confidence indices."""
    model_name: str
    model_version: str
    base_time: datetime
    lead_time_minutes: List[int] = Field(..., description="Forecast steps [10, 20, 30... 360]")
    forecast_grids: Optional[Any] = Field(None, description="Array of predicted reflectivity frames [T, H, W]")
    confidence_scores: List[float] = Field(..., description="Confidence index (0.0 to 1.0) for each lead time")
    metadata: Dict[str, Any] = Field(default_factory=dict)


class BaseNowcastModel(ABC):
    """Abstract interface for all 0-6 hour convective nowcasting models."""

    def __init__(self, model_name: str, model_version: str):
        self.model_name = model_name
        self.model_version = model_version

    @abstractmethod
    def load_weights(self, weights_path: str) -> None:
        """Loads model weights and calibration parameters from disk."""
        pass

    @abstractmethod
    def predict(self, input_sequence: np.ndarray, lead_times_minutes: List[int]) -> PredictionResult:
        """Generates future reflectivity prediction sequence given historical input radar frames."""
        pass


class OpticalFlowBaselineModel(BaseNowcastModel):
    """Lagrangian persistence / optical flow baseline model (e.g. pySTEPS extrapolation)."""

    def __init__(self):
        super().__init__(model_name="OpticalFlow-Baseline", model_version="0.1.0")

    def load_weights(self, weights_path: str) -> None:
        pass  # Non-parametric model

    def predict(self, input_sequence: np.ndarray, lead_times_minutes: List[int]) -> PredictionResult:
        # Standard baseline: persistence of latest frame with simulated advection decay
        last_frame = input_sequence[-1] if input_sequence.ndim >= 3 else input_sequence
        predictions = []
        confidences = []

        for lt in lead_times_minutes:
            conf = max(0.40, round(1.0 - (lt / 600.0), 2))
            confidences.append(conf)
            predictions.append(last_frame * conf)

        return PredictionResult(
            model_name=self.model_name,
            model_version=self.model_version,
            base_time=datetime.utcnow(),
            lead_time_minutes=lead_times_minutes,
            forecast_grids=np.array(predictions),
            confidence_scores=confidences,
            metadata={"extrapolation_method": "SEMI_LAGRANGIAN"},
        )
