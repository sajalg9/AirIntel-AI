from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import numpy as np
import torch
from torch import nn
from torch.utils.data import DataLoader, TensorDataset


class AQILSTMRegressor(nn.Module):
    def __init__(self, input_size: int, hidden_size: int = 64, num_layers: int = 2, dropout: float = 0.2):
        super().__init__()
        self.lstm = nn.LSTM(
            input_size=input_size,
            hidden_size=hidden_size,
            num_layers=num_layers,
            batch_first=True,
            dropout=dropout if num_layers > 1 else 0.0,
        )
        self.head = nn.Sequential(
            nn.Linear(hidden_size, hidden_size // 2),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_size // 2, 1),
        )

    def forward(self, inputs: torch.Tensor) -> torch.Tensor:
        outputs, _ = self.lstm(inputs)
        last_step = outputs[:, -1, :]
        return self.head(last_step).squeeze(-1)


@dataclass
class LSTMTrainingResult:
    model: AQILSTMRegressor
    history: list[dict[str, float]]


def create_dataloader(sequence_windows: np.ndarray, targets: np.ndarray, batch_size: int = 32, shuffle: bool = True) -> DataLoader:
    tensor_x = torch.tensor(sequence_windows, dtype=torch.float32)
    tensor_y = torch.tensor(targets, dtype=torch.float32)
    dataset = TensorDataset(tensor_x, tensor_y)
    return DataLoader(dataset, batch_size=batch_size, shuffle=shuffle)


def train_lstm_model(
    train_windows: np.ndarray,
    train_targets: np.ndarray,
    val_windows: np.ndarray | None,
    val_targets: np.ndarray | None,
    input_size: int,
    hidden_size: int = 64,
    num_layers: int = 2,
    dropout: float = 0.2,
    epochs: int = 20,
    batch_size: int = 32,
    learning_rate: float = 1e-3,
    device: str | None = None,
) -> LSTMTrainingResult:
    device = device or ("cuda" if torch.cuda.is_available() else "cpu")
    model = AQILSTMRegressor(input_size=input_size, hidden_size=hidden_size, num_layers=num_layers, dropout=dropout).to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)
    criterion = nn.HuberLoss()

    train_loader = create_dataloader(train_windows, train_targets, batch_size=batch_size, shuffle=True)
    val_loader = None
    if val_windows is not None and len(val_windows) > 0:
        val_loader = create_dataloader(val_windows, val_targets, batch_size=batch_size, shuffle=False)

    history: list[dict[str, float]] = []
    for epoch in range(epochs):
        model.train()
        train_loss = 0.0
        for batch_x, batch_y in train_loader:
            batch_x = batch_x.to(device)
            batch_y = batch_y.to(device)
            optimizer.zero_grad()
            predictions = model(batch_x)
            loss = criterion(predictions, batch_y)
            loss.backward()
            optimizer.step()
            train_loss += loss.item() * len(batch_x)

        train_loss /= max(1, len(train_loader.dataset))
        val_loss = float("nan")
        if val_loader is not None:
            model.eval()
            collected = 0.0
            with torch.no_grad():
                for batch_x, batch_y in val_loader:
                    batch_x = batch_x.to(device)
                    batch_y = batch_y.to(device)
                    predictions = model(batch_x)
                    loss = criterion(predictions, batch_y)
                    collected += loss.item() * len(batch_x)
            val_loss = collected / max(1, len(val_loader.dataset))

        history.append({"epoch": float(epoch + 1), "train_loss": float(train_loss), "val_loss": float(val_loss)})

    return LSTMTrainingResult(model=model, history=history)


def predict_lstm(model: AQILSTMRegressor, sequence_windows: np.ndarray, device: str | None = None) -> np.ndarray:
    device = device or ("cuda" if torch.cuda.is_available() else "cpu")
    model = model.to(device)
    model.eval()
    with torch.no_grad():
        tensor_x = torch.tensor(sequence_windows, dtype=torch.float32).to(device)
        predictions = model(tensor_x).detach().cpu().numpy()
    return predictions
