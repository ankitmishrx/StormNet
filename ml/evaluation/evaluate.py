"""Comparative Evaluation Pipeline for Nowcasting Baselines and Spatiotemporal U-Net."""

import json
import os
import argparse
from typing import Dict, Any, List, Tuple, Optional
import numpy as np
import torch

from ml.evaluation.evaluator import MeteorologicalSkillScoreEvaluator
from ml.inference.nowcast_model import OpticalFlowBaselineModel
from ml.models.unet import UNetNowcastModel


class NowcastingEvaluator:
    """Evaluates Persistence, Optical Flow, and U-Net on identical held-out test events."""

    def __init__(self, thresholds_dbz: List[float] = [20.0, 35.0, 45.0]):
        self.thresholds_dbz = thresholds_dbz
        self.metric_evaluator = MeteorologicalSkillScoreEvaluator()

    def evaluate_sequence(
        self,
        pred_grids: np.ndarray,   # (T_out, H, W) in dBZ
        target_grids: np.ndarray, # (T_out, H, W) in dBZ
    ) -> Dict[str, Any]:
        """Calculates CSI, POD, FAR, MAE, and RMSE across lead times and thresholds."""
        t_out = pred_grids.shape[0]

        # Continuous error metrics
        mae = float(np.mean(np.abs(pred_grids - target_grids)))
        rmse = float(np.sqrt(np.mean((pred_grids - target_grids) ** 2)))

        threshold_metrics = {}
        for th in self.thresholds_dbz:
            csi_steps = []
            pod_steps = []
            far_steps = []
            for t in range(t_out):
                m = self.metric_evaluator.evaluate(pred_grids[t], target_grids[t], threshold_dbz=th)
                csi_steps.append(m.critical_success_index)
                pod_steps.append(m.probability_of_detection)
                far_steps.append(m.false_alarm_ratio)

            threshold_metrics[f"threshold_{int(th)}dbz"] = {
                "mean_csi": round(float(np.mean(csi_steps)), 4),
                "mean_pod": round(float(np.mean(pod_steps)), 4),
                "mean_far": round(float(np.mean(far_steps)), 4),
                "csi_by_step": [round(v, 4) for v in csi_steps],
                "pod_by_step": [round(v, 4) for v in pod_steps],
            }

        return {
            "mae_dbz": round(mae, 3),
            "rmse_dbz": round(rmse, 3),
            "thresholds": threshold_metrics,
        }

    def evaluate_test_set(
        self,
        test_inputs: np.ndarray,   # (N, C, T_in, H, W)
        test_targets: np.ndarray,  # (N, T_out, H, W) in dBZ
        unet_model: Optional[UNetNowcastModel] = None,
        lead_times_minutes: Optional[List[int]] = None,
    ) -> Dict[str, Any]:
        """Evaluates Persistence, Optical Flow, and U-Net on identical test sequences."""
        lead_times = lead_times_minutes or [5, 10, 15, 20, 25, 30]
        n_samples = len(test_inputs)
        optical_flow = OpticalFlowBaselineModel()

        persistence_results = []
        optical_flow_results = []
        unet_results = []

        for i in range(n_samples):
            inp = test_inputs[i]
            tgt = test_targets[i]

            # 1. Persistence Baseline: Repeat last radar frame (channel 0, last timestep)
            last_radar = inp[0, -1]  # (H, W)
            pred_persist = np.repeat(last_radar[np.newaxis, :, :], len(lead_times), axis=0)
            res_persist = self.evaluate_sequence(pred_persist, tgt)
            persistence_results.append(res_persist)

            # 2. Optical Flow / Advection Baseline
            of_res = optical_flow.predict(inp[0], lead_times)
            pred_of = of_res.forecast_grids
            res_of = self.evaluate_sequence(pred_of, tgt)
            optical_flow_results.append(res_of)

            # 3. U-Net (if model provided)
            if unet_model:
                u_res = unet_model.predict(inp, lead_times)
                pred_unet = u_res.forecast_grids
                res_unet = self.evaluate_sequence(pred_unet, tgt)
                unet_results.append(res_unet)

        # Aggregate across all test samples
        def aggregate(metric_list: List[Dict[str, Any]]) -> Dict[str, Any]:
            if not metric_list:
                return {}
            mean_mae = float(np.mean([m["mae_dbz"] for m in metric_list]))
            mean_rmse = float(np.mean([m["rmse_dbz"] for m in metric_list]))

            agg_th = {}
            for th_key in metric_list[0]["thresholds"]:
                agg_th[th_key] = {
                    "csi": round(float(np.mean([m["thresholds"][th_key]["mean_csi"] for m in metric_list])), 4),
                    "pod": round(float(np.mean([m["thresholds"][th_key]["mean_pod"] for m in metric_list])), 4),
                    "far": round(float(np.mean([m["thresholds"][th_key]["mean_far"] for m in metric_list])), 4),
                }

            return {
                "mean_mae_dbz": round(mean_mae, 3),
                "mean_rmse_dbz": round(mean_rmse, 3),
                "skill_scores": agg_th,
            }

        comparison = {
            "evaluation_metadata": {
                "num_test_samples": n_samples,
                "lead_times_minutes": lead_times,
                "thresholds_evaluated": self.thresholds_dbz,
            },
            "persistence_baseline": aggregate(persistence_results),
            "optical_flow_baseline": aggregate(optical_flow_results),
            "spatiotemporal_unet": aggregate(unet_results) if unet_results else "NOT_EVALUATED",
        }

        return comparison
