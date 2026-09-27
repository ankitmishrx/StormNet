"""Reproducible Experiment Runner for Phase 6 Spatiotemporal U-Net Nowcasting."""

import json
import os
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Tuple, List, Dict, Any, Optional
import numpy as np
import torch

from ml.models.unet import UNetNowcastModel
from ml.training.splitter import EventBlockedSplitter, StormEpisode
from ml.training.train import ConvectiveSequenceDataset, train_nowcasting_model
from ml.evaluation.evaluate import NowcastingEvaluator
from ml.data.gating import enforce_experiment_safety_gate, ExperimentMode


def generate_controlled_convective_episodes(
    num_episodes: int = 4,
    timesteps_per_episode: int = 15,
    h: int = 64,
    w: int = 64,
    seed: int = 42,
) -> Tuple[np.ndarray, np.ndarray, List[StormEpisode]]:
    """Generates controlled convective storm sequences across distinct chronological episodes.

    Each episode represents a discrete convective day with moving storm cells and physical decay.
    """
    np.random.seed(seed)
    all_x = []
    all_y = []
    episodes = []

    base_time = datetime(2026, 7, 15, 12, 0, tzinfo=timezone.utc)
    current_index = 0

    for ep_id in range(num_episodes):
        # 48-hour separation between distinct convective episodes (strictly exceeding 24h embargo)
        ep_start = base_time + timedelta(days=ep_id * 2)
        ep_indices = []

        # Episode-specific cell kinematics
        cx = np.random.uniform(15, 30)
        cy = np.random.uniform(15, 30)
        vx = np.random.uniform(0.8, 1.8)
        vy = np.random.uniform(0.5, 1.5)
        peak_dbz = np.random.uniform(52.0, 62.0)

        # Generate sequence of volume states
        ep_frames = []
        for t in range(timesteps_per_episode + 10):
            # 4 channels: Radar (dBZ), Sat (K), Lightning (density), Wind (km/h)
            frame = np.zeros((4, h, w), dtype=np.float32)

            curr_cx = cx + vx * t
            curr_cy = cy + vy * t

            # 2D Gaussian convective core
            y_coords, x_coords = np.ogrid[:h, :w]
            dist_sq = (x_coords - curr_cx) ** 2 + (y_coords - curr_cy) ** 2
            core_mask = dist_sq < 144  # Radius 12 pixels

            # C0: Radar (0 to 75 dBZ)
            radar = np.maximum(0.0, peak_dbz * np.exp(-dist_sq / 72.0))
            frame[0] = radar

            # C1: Satellite Brightness Temp (150K to 350K, inverted core)
            sat = 295.0 - (radar / 75.0) * 80.0
            frame[1] = sat

            # C2: Lightning Density (strikes/km^2)
            frame[2] = np.where(radar >= 35.0, (radar - 35.0) / 10.0, 0.0)

            # C3: Surface Wind Speed (km/h)
            frame[3] = 15.0 + (radar / 75.0) * 35.0

            ep_frames.append(frame)

        # Extract (T_in=4, T_out=6) pairs
        t_in = 4
        t_out = 6
        for i in range(len(ep_frames) - (t_in + t_out)):
            x_seq = np.array(ep_frames[i : i + t_in])  # (T_in, C, H, W)
            x_seq = np.transpose(x_seq, (1, 0, 2, 3))  # (C, T_in, H, W)

            # Target: Future radar reflectivity (C0) in dBZ
            y_seq = np.array([ep_frames[i + t_in + k][0] for k in range(t_out)])  # (T_out, H, W)

            # Normalize inputs
            x_norm = np.copy(x_seq)
            x_norm[0] = np.clip(x_norm[0] / 75.0, 0, 1)                  # Radar [0, 1]
            x_norm[1] = np.clip((350.0 - x_norm[1]) / 200.0, 0, 1)       # Sat [0, 1]
            x_norm[2] = np.clip(x_norm[2] / 10.0, 0, 1)                  # Lightning [0, 1]
            x_norm[3] = np.clip(x_norm[3] / 100.0, 0, 1)                 # Wind [0, 1]

            y_norm = np.clip(y_seq / 75.0, 0, 1)  # Target normalized for loss calculation

            all_x.append(x_norm)
            all_y.append(y_norm)
            ep_indices.append(current_index)
            current_index += 1

        ep_end = ep_start + timedelta(minutes=timesteps_per_episode * 5)
        episodes.append(
            StormEpisode(
                episode_id=f"EPISODE-NCR-2026-07-{ep_id+1:02d}",
                start_time=ep_start,
                end_time=ep_end,
                sector_id="delhi-ncr",
                sequence_count=len(ep_indices),
                sample_indices=ep_indices,
            )
        )

    return np.array(all_x), np.array(all_y), episodes


def run_phase6_experiment(
    experiment_id: str = "exp_001_spatiotemporal_unet",
    epochs: int = 10,
    device: str = "cpu",
    mode: str = ExperimentMode.DEVELOPMENT_TEST.value,
) -> Dict[str, Any]:
    """Runs complete Phase 6 nowcasting training and held-out evaluation."""
    # Enforce scientific validation safety gate
    enforce_experiment_safety_gate(dataset_provenance="SYNTHETIC_DATA", experiment_mode=mode)

    print("==================================================")
    print("STORMNET PHASE 6 — NOWCASTING EXPERIMENT PIPELINE")
    print("==================================================")
    exp_dir = os.path.join("experiments", experiment_id)
    os.makedirs(exp_dir, exist_ok=True)

    # 1. Dataset Generation & Event Partitioning
    print("\n[1/4] Assembling Controlled Convective Episodes...")
    x_data, y_data, episodes = generate_controlled_convective_episodes()
    print(f"      Total Sequences : {len(x_data)} | Episodes: {len(episodes)}")

    # 2. Event-Blocked Split with 24h Embargo
    print("\n[2/4] Executing Event-Blocked Split (24h Embargo)...")
    splitter = EventBlockedSplitter(embargo_hours=24.0, train_ratio=0.50, val_ratio=0.25, test_ratio=0.25)
    splits = splitter.partition_episodes(episodes)

    print(f"      Train Episodes : {splits.train_episodes} ({len(splits.train_indices)} samples)")
    print(f"      Val Episodes   : {splits.val_episodes} ({len(splits.val_indices)} samples)")
    print(f"      Test Episodes  : {splits.test_episodes} ({len(splits.test_indices)} samples)")

    train_ds = ConvectiveSequenceDataset(x_data[splits.train_indices], y_data[splits.train_indices])
    val_ds = ConvectiveSequenceDataset(x_data[splits.val_indices], y_data[splits.val_indices])

    # 3. Model Training
    print("\n[3/4] Training Spatiotemporal U-Net...")
    config = {
        "model": "SpatiotemporalUNet",
        "in_channels": 16,     # 4 vars * 4 timesteps
        "out_timesteps": 6,    # +5 to +30 min
        "base_features": 24,   # Lightweight for fast CPU inference
        "batch_size": 4,
        "learning_rate": 2e-3,
        "weight_decay": 1e-5,
        "epochs": epochs,
        "seed": 42,
    }

    train_meta = train_nowcasting_model(
        train_dataset=train_ds,
        val_dataset=val_ds,
        config=config,
        experiment_dir=exp_dir,
        device=device,
    )

    # 4. Held-Out Evaluation on Unseen Test Events
    print("\n[4/4] Evaluating Baselines & U-Net on Unseen Test Split...")
    test_x = x_data[splits.test_indices]
    # Denormalize test targets back to dBZ for standard meteorological skill evaluation
    test_y_dbz = y_data[splits.test_indices] * 75.0

    best_ckpt = os.path.join(exp_dir, "best_unet_model.pt")
    unet_wrapper = UNetNowcastModel(
        weights_path=best_ckpt,
        in_channels=16,
        out_timesteps=6,
        base_features=24,
        device=device,
    )

    evaluator = NowcastingEvaluator(thresholds_dbz=[20.0, 35.0, 45.0])
    eval_results = evaluator.evaluate_test_set(
        test_inputs=test_x,
        test_targets=test_y_dbz,
        unet_model=unet_wrapper,
        lead_times_minutes=[5, 10, 15, 20, 25, 30],
    )

    # Save full evaluation report
    report = {
        "experiment_id": experiment_id,
        "executed_at": datetime.now(timezone.utc).isoformat(),
        "train_metadata": train_meta,
        "splits": {
            "train_episodes": splits.train_episodes,
            "val_episodes": splits.val_episodes,
            "test_episodes": splits.test_episodes,
            "embargo_hours": splits.embargo_hours,
        },
        "comparative_evaluation": eval_results,
    }

    report_path = os.path.join(exp_dir, "evaluation_report.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    print("\n==================================================")
    print("PHASE 6 EXPERIMENT COMPLETED")
    print("==================================================")
    print(f"Artifacts saved to : {exp_dir}")
    print(f"Evaluation report  : {report_path}")

    return report


if __name__ == "__main__":
    run_phase6_experiment(epochs=10)
