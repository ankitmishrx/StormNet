"""Training pipeline for Spatiotemporal U-Net Convective Nowcasting."""

import argparse
import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, Tuple, Optional, List
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader

from ml.models.unet import SpatiotemporalUNet
from ml.training.splitter import EventBlockedSplitter, StormEpisode


class ConvectiveSequenceDataset(Dataset):
    """Dataset providing paired (X_t, Y_t) spatio-temporal tensor sequences."""

    def __init__(
        self,
        features: np.ndarray,  # Shape (N, C, T_in, H, W)
        targets: np.ndarray,   # Shape (N, T_out, H, W)
    ):
        self.features = torch.from_numpy(features).float()
        self.targets = torch.from_numpy(targets).float()

    def __len__(self) -> int:
        return len(self.features)

    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, torch.Tensor]:
        return self.features[idx], self.targets[idx]


class WeightedMSELoss(nn.Module):
    """Meteorologically weighted MSE emphasizing severe reflectivity cores (dBZ >= 35)."""

    def __init__(self, heavy_rain_weight: float = 3.0, severe_core_weight: float = 5.0):
        super().__init__()
        self.heavy_weight = heavy_rain_weight
        self.severe_weight = severe_core_weight

    def forward(self, pred: torch.Tensor, target: torch.Tensor) -> torch.Tensor:
        # Base squared error
        diff_sq = (pred - target) ** 2

        # Weighting mask based on target reflectivity (normalized [0, 1])
        # 35 dBZ / 75 = ~0.47, 45 dBZ / 75 = 0.60
        weights = torch.ones_like(target)
        weights = torch.where(target >= 0.47, weights * self.heavy_weight, weights)
        weights = torch.where(target >= 0.60, weights * self.severe_weight, weights)

        weighted_loss = torch.mean(weights * diff_sq)
        return weighted_loss


def train_nowcasting_model(
    train_dataset: Dataset,
    val_dataset: Dataset,
    config: Dict[str, Any],
    experiment_dir: str,
    device: str = "cpu",
) -> Dict[str, Any]:
    """Executes deterministic training loop with validation monitoring and checkpointing."""
    seed = config.get("seed", 42)
    torch.manual_seed(seed)
    np.random.seed(seed)

    dev = torch.device(device)
    os.makedirs(experiment_dir, exist_ok=True)

    # Initialize Model
    model = SpatiotemporalUNet(
        in_channels=config.get("in_channels", 16),
        out_timesteps=config.get("out_timesteps", 6),
        base_features=config.get("base_features", 32),
    ).to(dev)

    criterion = WeightedMSELoss()
    optimizer = torch.optim.Adam(
        model.parameters(),
        lr=config.get("learning_rate", 1e-3),
        weight_decay=config.get("weight_decay", 1e-5),
    )

    batch_size = config.get("batch_size", 4)
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False) if len(val_dataset) > 0 else None

    epochs = config.get("epochs", 15)
    best_val_loss = float("inf")
    history = {"train_loss": [], "val_loss": []}

    print(f"Starting training: {epochs} epochs | Parameters: {model.get_parameter_count():,}")
    t0 = time.perf_counter()

    for epoch in range(1, epochs + 1):
        model.train()
        running_train_loss = 0.0

        for batch_x, batch_y in train_loader:
            batch_x, batch_y = batch_x.to(dev), batch_y.to(dev)
            optimizer.zero_grad()
            preds = model(batch_x)
            loss = criterion(preds, batch_y)
            loss.backward()
            optimizer.step()
            running_train_loss += loss.item() * len(batch_x)

        avg_train_loss = running_train_loss / len(train_dataset)
        history["train_loss"].append(round(avg_train_loss, 6))

        # Validation step
        avg_val_loss = avg_train_loss  # Default if no val split
        if val_loader:
            model.eval()
            running_val_loss = 0.0
            with torch.no_grad():
                for val_x, val_y in val_loader:
                    val_x, val_y = val_x.to(dev), val_y.to(dev)
                    v_preds = model(val_x)
                    v_loss = criterion(v_preds, val_y)
                    running_val_loss += v_loss.item() * len(val_x)
            avg_val_loss = running_val_loss / len(val_dataset)
            history["val_loss"].append(round(avg_val_loss, 6))

        print(f"Epoch [{epoch:02d}/{epochs:02d}] - Train Loss: {avg_train_loss:.5f} | Val Loss: {avg_val_loss:.5f}")

        # Checkpoint if best
        if avg_val_loss < best_val_loss:
            best_val_loss = avg_val_loss
            best_ckpt_path = os.path.join(experiment_dir, "best_unet_model.pt")
            torch.save(
                {
                    "epoch": epoch,
                    "model_state_dict": model.state_dict(),
                    "optimizer_state_dict": optimizer.state_dict(),
                    "val_loss": best_val_loss,
                    "config": config,
                    "saved_at": datetime.now(timezone.utc).isoformat(),
                },
                best_ckpt_path,
            )

    train_duration_s = time.perf_counter() - t0

    # Save final artifacts
    meta = {
        "experiment_id": Path(experiment_dir).name,
        "model_architecture": "SpatiotemporalUNet",
        "parameter_count": model.get_parameter_count(),
        "epochs_trained": epochs,
        "best_val_loss": round(best_val_loss, 6),
        "total_training_duration_seconds": round(train_duration_s, 2),
        "training_history": history,
        "config": config,
        "completed_at": datetime.now(timezone.utc).isoformat(),
    }

    with open(os.path.join(experiment_dir, "training_summary.json"), "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)

    return meta
