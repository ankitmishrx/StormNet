"""Unit tests verifying ML modules, feature extraction, and data source adapters."""

import pytest
import numpy as np
from ml.features.feature_pipeline import ConvectiveFeatureExtractor
from ml.inference.nowcast_model import OpticalFlowBaselineModel
from ml.inference.tracker import CentroidStormTracker
from ml.evaluation.evaluator import MeteorologicalSkillScoreEvaluator
from packages.shared.data_sources.radar import MockRadarAdapter
from packages.shared.data_sources.satellite import MockSatelliteAdapter
from packages.shared.data_sources.lightning import MockLightningAdapter
from packages.shared.data_sources.surface_obs import MockSurfaceObsAdapter


def test_convective_feature_extractor():
    """Verifies VIL and Echo Top calculation functions."""
    extractor = ConvectiveFeatureExtractor()
    # 3D test radar volume: 5 vertical levels, 10x10 grid
    vol = np.full((5, 10, 10), 45.0)
    vil = extractor.calculate_vil(vol, delta_z_km=1.0)
    assert vil.shape == (10, 10)
    assert np.all(vil > 0)

    echo_tops = extractor.calculate_echo_tops(vol, [1.0, 3.0, 5.0, 8.0, 12.0])
    assert echo_tops.shape == (10, 10)
    assert np.all(echo_tops == 12.0)


def test_optical_flow_baseline_model():
    """Verifies baseline nowcasting model produces expected lead times and confidence decay."""
    model = OpticalFlowBaselineModel()
    dummy_input = np.ones((4, 20, 20)) * 50.0
    result = model.predict(dummy_input, lead_times_minutes=[15, 30, 60, 120])

    assert result.model_name == "OpticalFlow-Baseline"
    assert len(result.lead_time_minutes) == 4
    assert len(result.confidence_scores) == 4
    # Confidence must monotonically decrease over lead time
    assert result.confidence_scores[0] > result.confidence_scores[-1]


def test_storm_tracker():
    """Verifies cell segmentation and vector extrapolation."""
    tracker = CentroidStormTracker()
    grid = np.zeros((50, 50))
    grid[20:30, 20:30] = 55.0  # Synthetic convective core

    cells = tracker.segment_cells(grid, dbz_threshold=40.0)
    assert len(cells) == 1
    assert cells[0]["max_dbz"] == 55.0

    tracked = tracker.track_and_extrapolate(cells, [], [15, 30, 45, 60])
    assert len(tracked) == 1
    assert len(tracked[0].projected_centroids) == 4


def test_meteorological_skill_score_evaluator():
    """Verifies POD, FAR, CSI, and ETS calculations."""
    evaluator = MeteorologicalSkillScoreEvaluator()
    # Perfect forecast scenario: pred == obs
    pred = np.array([[50.0, 20.0], [10.0, 60.0]])
    obs = np.array([[50.0, 20.0], [10.0, 60.0]])

    metrics = evaluator.evaluate(pred, obs, threshold_dbz=40.0)
    assert metrics.probability_of_detection == 1.0
    assert metrics.false_alarm_ratio == 0.0
    assert metrics.critical_success_index == 1.0


@pytest.mark.asyncio
async def test_mock_data_sources():
    """Verifies mock adapters adhere to BaseDataSource contracts."""
    radar = MockRadarAdapter()
    sat = MockSatelliteAdapter()
    ltg = MockLightningAdapter()
    aws = MockSurfaceObsAdapter()

    for adapter in [radar, sat, ltg, aws]:
        health = await adapter.check_health()
        assert health.status.value == "ONLINE"

        latest = await adapter.fetch_latest()
        assert latest.success is True
        assert latest.data is not None
