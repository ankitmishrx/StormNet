"""Meteorological validation metrics and model evaluator interface."""

from abc import ABC, abstractmethod
from typing import Dict, Any
from pydantic import BaseModel
import numpy as np


class ContingencyTable(BaseModel):
    """Standard 2x2 dichotomous meteorological contingency matrix."""
    hits: int = 0  # Event forecast and observed
    misses: int = 0  # Event observed but not forecast
    false_alarms: int = 0  # Event forecast but not observed
    correct_negatives: int = 0  # Event neither forecast nor observed


class VerificationMetrics(BaseModel):
    """Standard meteorological verification scores."""
    probability_of_detection: float  # POD = Hits / (Hits + Misses)
    false_alarm_ratio: float  # FAR = FalseAlarms / (Hits + FalseAlarms)
    critical_success_index: float  # CSI = Hits / (Hits + Misses + FalseAlarms)
    equitable_threat_score: float  # ETS
    frequency_bias: float  # FBIAS = (Hits + FalseAlarms) / (Hits + Misses)


class ModelEvaluator(ABC):
    """Abstract interface for verifying nowcasting accuracy against ground-truth radar sweeps."""

    @abstractmethod
    def evaluate(
        self,
        predicted_grid: np.ndarray,
        ground_truth_grid: np.ndarray,
        threshold_dbz: float,
    ) -> VerificationMetrics:
        """Evaluates prediction grid against ground truth at a specific dBZ threshold (e.g. 35 or 45 dBZ)."""
        pass


class MeteorologicalSkillScoreEvaluator(ModelEvaluator):
    """Computes POD, FAR, CSI, and ETS from predicted and observed reflectivity grids."""

    def compute_contingency(
        self,
        predicted_grid: np.ndarray,
        ground_truth_grid: np.ndarray,
        threshold_dbz: float,
    ) -> ContingencyTable:
        pred_event = predicted_grid >= threshold_dbz
        obs_event = ground_truth_grid >= threshold_dbz

        hits = int(np.sum(pred_event & obs_event))
        misses = int(np.sum(~pred_event & obs_event))
        false_alarms = int(np.sum(pred_event & ~obs_event))
        correct_negatives = int(np.sum(~pred_event & ~obs_event))

        return ContingencyTable(
            hits=hits,
            misses=misses,
            false_alarms=false_alarms,
            correct_negatives=correct_negatives,
        )

    def evaluate(
        self,
        predicted_grid: np.ndarray,
        ground_truth_grid: np.ndarray,
        threshold_dbz: float = 35.0,
    ) -> VerificationMetrics:
        table = self.compute_contingency(predicted_grid, ground_truth_grid, threshold_dbz)
        h, m, f, c = table.hits, table.misses, table.false_alarms, table.correct_negatives

        total = h + m + f + c
        if total == 0:
            return VerificationMetrics(
                probability_of_detection=0.0,
                false_alarm_ratio=0.0,
                critical_success_index=0.0,
                equitable_threat_score=0.0,
                frequency_bias=1.0,
            )

        pod = h / (h + m) if (h + m) > 0 else 0.0
        far = f / (h + f) if (h + f) > 0 else 0.0
        csi = h / (h + m + f) if (h + m + f) > 0 else 0.0
        fbias = (h + f) / (h + m) if (h + m) > 0 else 1.0

        # Random hits expected by chance
        hits_random = ((h + m) * (h + f)) / total if total > 0 else 0.0
        ets_denom = (h + m + f - hits_random)
        ets = (h - hits_random) / ets_denom if ets_denom > 0 else 0.0

        return VerificationMetrics(
            probability_of_detection=round(pod, 4),
            false_alarm_ratio=round(far, 4),
            critical_success_index=round(csi, 4),
            equitable_threat_score=round(ets, 4),
            frequency_bias=round(fbias, 4),
        )
