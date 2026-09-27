"""Spatiotemporal U-Net Architecture for Convective Scale Radar Nowcasting."""

import os
from typing import Dict, Any, List, Optional, Tuple
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

from ml.inference.nowcast_model import BaseNowcastModel, PredictionResult
from datetime import datetime, timezone


class DoubleConv(nn.Module):
    """(Convolution => BatchNorm => LeakyReLU) * 2."""

    def __init__(self, in_channels: int, out_channels: int):
        super().__init__()
        self.double_conv = nn.Sequential(
            nn.Conv2d(in_channels, out_channels, kernel_size=3, padding=1, bias=False),
            nn.BatchNorm2d(out_channels),
            nn.LeakyReLU(0.1, inplace=True),
            nn.Conv2d(out_channels, out_channels, kernel_size=3, padding=1, bias=False),
            nn.BatchNorm2d(out_channels),
            nn.LeakyReLU(0.1, inplace=True),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.double_conv(x)


class SpatiotemporalUNet(nn.Module):
    """Lightweight 2D-Temporal U-Net for convective radar extrapolation.

    Input shape : (B, C * T_in, H, W) or (B, C, T_in, H, W)
    Output shape: (B, T_out, H, W) where values are normalized reflectivity [0, 1].
    """

    def __init__(
        self,
        in_channels: int = 16,  # 4 variables * 4 timesteps = 16
        out_timesteps: int = 6,  # 6 future lead times (+5 to +30 min)
        base_features: int = 32,
    ):
        super().__init__()
        self.in_channels = in_channels
        self.out_timesteps = out_timesteps
        self.base_features = base_features

        f = base_features  # 32

        # Encoder
        self.inc = DoubleConv(in_channels, f)             # 16 -> 32
        self.down1 = nn.Sequential(nn.MaxPool2d(2), DoubleConv(f, f * 2))       # 32 -> 64
        self.down2 = nn.Sequential(nn.MaxPool2d(2), DoubleConv(f * 2, f * 4))   # 64 -> 128
        self.down3 = nn.Sequential(nn.MaxPool2d(2), DoubleConv(f * 4, f * 4))   # 128 -> 128 (bottleneck)

        # Decoder with skip connections
        self.up1 = nn.ConvTranspose2d(f * 4, f * 4, kernel_size=2, stride=2)
        self.conv_up1 = DoubleConv(f * 8, f * 2)                                 # 128 + 128 -> 64

        self.up2 = nn.ConvTranspose2d(f * 2, f * 2, kernel_size=2, stride=2)
        self.conv_up2 = DoubleConv(f * 4, f)                                     # 64 + 64 -> 32

        self.up3 = nn.ConvTranspose2d(f, f, kernel_size=2, stride=2)
        self.conv_up3 = DoubleConv(f * 2, f)                                     # 32 + 32 -> 32

        # Output Head: projects to out_timesteps frames
        self.outc = nn.Sequential(
            nn.Conv2d(f, out_timesteps, kernel_size=1),
            nn.Sigmoid(),  # Reflectivity normalized to [0, 1]
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # If input has shape (B, C, T, H, W), flatten channel and temporal dimensions
        if x.dim() == 5:
            b, c, t, h, w = x.shape
            x = x.view(b, c * t, h, w)

        x1 = self.inc(x)
        x2 = self.down1(x1)
        x3 = self.down2(x2)
        x4 = self.down3(x3)

        u1 = self.up1(x4)
        # Pad if odd dimensions
        if u1.shape[-2:] != x3.shape[-2:]:
            u1 = F.interpolate(u1, size=x3.shape[-2:], mode="bilinear", align_corners=False)
        d1 = self.conv_up1(torch.cat([u1, x3], dim=1))

        u2 = self.up2(d1)
        if u2.shape[-2:] != x2.shape[-2:]:
            u2 = F.interpolate(u2, size=x2.shape[-2:], mode="bilinear", align_corners=False)
        d2 = self.conv_up2(torch.cat([u2, x2], dim=1))

        u3 = self.up3(d2)
        if u3.shape[-2:] != x1.shape[-2:]:
            u3 = F.interpolate(u3, size=x1.shape[-2:], mode="bilinear", align_corners=False)
        d3 = self.conv_up3(torch.cat([u3, x1], dim=1))

        out = self.outc(d3)
        return out

    def get_parameter_count(self) -> int:
        return sum(p.numel() for p in self.parameters() if p.requires_grad)


class UNetNowcastModel(BaseNowcastModel):
    """Inference wrapper for the Spatiotemporal U-Net nowcasting model."""

    def __init__(
        self,
        weights_path: Optional[str] = None,
        in_channels: int = 16,
        out_timesteps: int = 6,
        base_features: int = 32,
        device: str = "cpu",
    ):
        super().__init__(model_name="StormNet-Spatiotemporal-UNet", model_version="1.0.0")
        self.device = torch.device(device)
        self.out_timesteps = out_timesteps
        self.in_channels = in_channels

        # Inspect checkpoint if provided to ensure matching base_features
        if weights_path and os.path.exists(weights_path):
            checkpoint = torch.load(weights_path, map_location=self.device)
            state_dict = checkpoint["model_state_dict"] if "model_state_dict" in checkpoint else checkpoint
            if "outc.0.weight" in state_dict:
                base_features = state_dict["outc.0.weight"].shape[1]
            self.model = SpatiotemporalUNet(
                in_channels=in_channels,
                out_timesteps=out_timesteps,
                base_features=base_features,
            ).to(self.device)
            self.model.load_state_dict(state_dict)
        else:
            self.model = SpatiotemporalUNet(
                in_channels=in_channels,
                out_timesteps=out_timesteps,
                base_features=base_features,
            ).to(self.device)

        self.model.eval()

    def load_weights(self, weights_path: str) -> None:
        """Loads state dict from disk."""
        checkpoint = torch.load(weights_path, map_location=self.device)
        state_dict = checkpoint["model_state_dict"] if "model_state_dict" in checkpoint else checkpoint
        if "outc.0.weight" in state_dict:
            base_features = state_dict["outc.0.weight"].shape[1]
            self.model = SpatiotemporalUNet(
                in_channels=self.in_channels,
                out_timesteps=self.out_timesteps,
                base_features=base_features,
            ).to(self.device)
        self.model.load_state_dict(state_dict)
        self.model.eval()

    def predict(
        self,
        input_sequence: np.ndarray,
        lead_times_minutes: Optional[List[int]] = None,
    ) -> PredictionResult:
        """Runs forward pass on input sequence and rescales reflectivity to dBZ.

        Input: numpy array of shape (C, T, H, W) or (T, H, W) or (C*T, H, W)
        Output: PredictionResult container
        """
        lead_times = lead_times_minutes or [5, 10, 15, 20, 25, 30]

        # Convert to tensor with batch dimension
        if isinstance(input_sequence, np.ndarray):
            tensor_in = torch.from_numpy(input_sequence).float()
        else:
            tensor_in = input_sequence.float()

        if tensor_in.dim() == 3:
            # (T, H, W) -> (1, 1*T, H, W)
            tensor_in = tensor_in.unsqueeze(0)
        elif tensor_in.dim() == 4:
            # (C, T, H, W) -> (1, C, T, H, W)
            tensor_in = tensor_in.unsqueeze(0)

        tensor_in = tensor_in.to(self.device)

        with torch.no_grad():
            # Normalized prediction [0, 1]
            pred_norm = self.model(tensor_in)  # (1, T_out, H, W)
            pred_dbz = pred_norm * 75.0        # Rescale to dBZ [0, 75]

        pred_np = pred_dbz.squeeze(0).cpu().numpy()  # (T_out, H, W)

        # Slice or pad to requested lead times
        if len(lead_times) <= pred_np.shape[0]:
            out_grids = pred_np[: len(lead_times)]
        else:
            # Persistence padding if more lead times requested than model horizon
            pad_len = len(lead_times) - pred_np.shape[0]
            last_grid = pred_np[-1:]
            padding = np.repeat(last_grid, pad_len, axis=0) * 0.95
            out_grids = np.concatenate([pred_np, padding], axis=0)

        # Confidence scores decaying with lead time
        confidences = [max(0.35, round(1.0 - (lt / 360.0) * 0.65, 2)) for lt in lead_times]

        return PredictionResult(
            model_name=self.model_name,
            model_version=self.model_version,
            base_time=datetime.now(timezone.utc),
            lead_time_minutes=lead_times,
            forecast_grids=out_grids,
            confidence_scores=confidences,
            metadata={
                "architecture": "Spatiotemporal-UNet",
                "param_count": self.model.get_parameter_count(),
                "device": str(self.device),
                "validated_horizon_minutes": min(30, max(lead_times)),
            },
        )
