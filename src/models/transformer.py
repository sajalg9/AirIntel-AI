from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import torch
from torch import nn
from torch.utils.data import DataLoader, TensorDataset


class PositionalEncoding(nn.Module):
    def __init__(self, d_model: int, max_len: int = 512):
        super().__init__()
        positions = torch.arange(max_len).unsqueeze(1)
        div_term = torch.exp(torch.arange(0, d_model, 2) * (-torch.log(torch.tensor(10000.0)) / d_model))
        encoding = torch.zeros(max_len, d_model)
        encoding[:, 0::2] = torch.sin(positions.float() * div_term)
        encoding[:, 1::2] = torch.cos(positions.float() * div_term)
        self.register_buffer("encoding", encoding.unsqueeze(0))

    def forward(self, inputs: torch.Tensor) -> torch.Tensor:
        return inputs + self.encoding[:, : inputs.size(1)]


class AQITransformerRegressor(nn.Module):
    def __init__(self, input_size: int, d_model: int = 64, nhead: int = 4, num_layers: int = 2, dropout: float = 0.2):
        super().__init__()
        self.input_projection = nn.Linear(input_size, d_model)
        self.positional_encoding = PositionalEncoding(d_model)
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=d_model,
            nhead=nhead,
            dim_feedforward=d_model * 2,
            dropout=dropout,
            batch_first=True,
            activation="gelu",
        )
        self.encoder = nn.TransformerEncoder(encoder_layer, num_layers=num_layers)
        self.head = nn.Sequential(
            nn.Linear(d_model, d_model // 2),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(d_model // 2, 1),
        )

    def forward(self, inputs: torch.Tensor) -> torch.Tensor:
        projected = self.input_projection(inputs)
        encoded = self.positional_encoding(projected)
        encoded = self.encoder(encoded)
        pooled = encoded.mean(dim=1)
        return self.head(pooled).squeeze(-1)


@dataclass
class TransformerTrainingResult:
    model: AQITransformerRegressor
    history: list[dict[str, float]]


def create_dataloader(sequence_windows: np.ndarray, targets: np.ndarray, batch_size: int = 32, shuffle: bool = True) -> DataLoader:
    tensor_x = torch.tensor(sequence_windows, dtype=torch.float32)
    tensor_y = torch.tensor(targets, dtype=torch.float32)
    dataset = TensorDataset(tensor_x, tensor_y)
    return DataLoader(dataset, batch_size=batch_size, shuffle=shuffle)


def train_transformer_model(
    train_windows: np.ndarray,
    train_targets: np.ndarray,
    val_windows: np.ndarray | None,
    val_targets: np.ndarray | None,
    input_size: int,
    d_model: int = 64,
    nhead: int = 4,
    num_layers: int = 2,
    dropout: float = 0.2,
    epochs: int = 20,
    batch_size: int = 32,
    learning_rate: float = 1e-3,
    device: str | None = None,
) -> TransformerTrainingResult:
    device = device or ("cuda" if torch.cuda.is_available() else "cpu")
    model = AQITransformerRegressor(
        input_size=input_size,
        d_model=d_model,
        nhead=nhead,
        num_layers=num_layers,
        dropout=dropout,
    ).to(device)
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

    return TransformerTrainingResult(model=model, history=history)


def predict_transformer(model: AQITransformerRegressor, sequence_windows: np.ndarray, device: str | None = None) -> np.ndarray:
    device = device or ("cuda" if torch.cuda.is_available() else "cpu")
    model = model.to(device)
    model.eval()
    with torch.no_grad():
        tensor_x = torch.tensor(sequence_windows, dtype=torch.float32).to(device)
        predictions = model(tensor_x).detach().cpu().numpy()
    return predictions
