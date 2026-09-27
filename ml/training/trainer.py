"""Base model training interfaces and configurations for nowcasting models."""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from pydantic import BaseModel


class TrainingConfig(BaseModel):
    """Hyperparameter and operational configuration for nowcasting model training."""
    model_architecture: str  # e.g., ConvLSTM, MetNet, PredRNN, UNet3D
    sequence_input_length: int = 4  # 4 past frames (-40m to T-0)
    sequence_output_length: int = 24  # 24 future frames (+10m to +4h)
    batch_size: int = 16
    learning_rate: float = 1e-4
    epochs: int = 50
    loss_function: str = "BMA_Weighted_MSE"  # Balanced Mean Absolute / Critical Loss
    checkpoint_dir: str = "./ml/checkpoints"


class BaseModelTrainer(ABC):
    """Abstract interface orchestrating spatio-temporal model training and validation."""

    def __init__(self, config: TrainingConfig):
        self.config = config

    @abstractmethod
    def build_model(self) -> Any:
        """Initializes neural network architecture layers."""
        pass

    @abstractmethod
    def train_epoch(self, dataloader: Any) -> float:
        """Executes forward pass, backpropagation, and loss calculation for a single epoch."""
        pass

    @abstractmethod
    def validate(self, val_dataloader: Any) -> Dict[str, float]:
        """Evaluates model performance against validation split using meteorological metrics."""
        pass
