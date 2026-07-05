from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
import torch
from sklearn.ensemble import RandomForestRegressor

from ..preprocessing import PreprocessingArtifacts, latest_sequence_for_city, transform_dataframe
from .lstm import AQILSTMRegressor, predict_lstm
from .transformer import AQITransformerRegressor, predict_transformer


@dataclass
class LoadedModels:
    artifacts: PreprocessingArtifacts
    random_forest: Any | None = None
    xgboost: Any | None = None
    lstm: AQILSTMRegressor | None = None
    transformer: AQITransformerRegressor | None = None
    metrics: dict[str, Any] | None = None


def _load_torch_model(path: Path, model: torch.nn.Module, device: str | None = None) -> torch.nn.Module:
    device = device or ("cuda" if torch.cuda.is_available() else "cpu")
    state_dict = torch.load(path, map_location=device)
    model.load_state_dict(state_dict)
    return model.to(device)


def load_artifacts(model_dir: str | Path) -> LoadedModels:
    model_dir = Path(model_dir)
    artifacts = joblib.load(model_dir / "preprocessing.joblib")
    metrics_path = model_dir / "training_metrics.json"
    metrics = None
    if metrics_path.exists():
        import json

        metrics = json.loads(metrics_path.read_text(encoding="utf-8"))

    random_forest = None
    rf_path = model_dir / "random_forest.joblib"
    if rf_path.exists():
        random_forest = joblib.load(rf_path)

    xgboost_model = None
    xgb_path = model_dir / "xgboost.joblib"
    if xgb_path.exists():
        xgboost_model = joblib.load(xgb_path)

    lstm_model = None
    lstm_path = model_dir / "lstm.pt"
    if lstm_path.exists():
        lstm_model = AQILSTMRegressor(input_size=len(artifacts.feature_columns)).cpu()
        lstm_model = _load_torch_model(lstm_path, lstm_model)

    transformer_model = None
    transformer_path = model_dir / "transformer.pt"
    if transformer_path.exists():
        transformer_model = AQITransformerRegressor(input_size=len(artifacts.feature_columns)).cpu()
        transformer_model = _load_torch_model(transformer_path, transformer_model)

    return LoadedModels(
        artifacts=artifacts,
        random_forest=random_forest,
        xgboost=xgboost_model,
        lstm=lstm_model,
        transformer=transformer_model,
        metrics=metrics,
    )


def recursive_forecast(
    df,
    loaded: LoadedModels,
    city: str,
    model_name: str = "transformer",
    horizon: int = 7,
) -> tuple[list[dict[str, Any]], np.ndarray]:
    sequence_window, recent_frame = latest_sequence_for_city(df, loaded.artifacts, city)
    predictions: list[dict[str, Any]] = []
    working_window = sequence_window.copy()

    for _ in range(horizon):
        if model_name == "random_forest" and loaded.random_forest is not None:
            flat_window = working_window.reshape(1, -1)
            predicted_scaled = float(loaded.random_forest.predict(flat_window)[0])
        elif model_name == "xgboost" and loaded.xgboost is not None:
            flat_window = working_window.reshape(1, -1)
            predicted_scaled = float(loaded.xgboost.predict(flat_window)[0])
        elif model_name == "lstm" and loaded.lstm is not None:
            predicted_scaled = float(predict_lstm(loaded.lstm, working_window[None, ...])[0])
        elif model_name == "transformer" and loaded.transformer is not None:
            predicted_scaled = float(predict_transformer(loaded.transformer, working_window[None, ...])[0])
        else:
            predicted_scaled = float(np.mean(working_window[-3:, 0]))

        predicted_aqi = float(loaded.artifacts.target_scaler.inverse_transform([[predicted_scaled]])[0, 0])
        next_date = pd.Timestamp(recent_frame.iloc[-1]["Date"]) + pd.Timedelta(days=1)
        last_row = recent_frame.iloc[-1].copy()
        last_row["AQI"] = predicted_aqi
        last_row["Date"] = next_date
        predictions.append({"date": pd.Timestamp(next_date).to_pydatetime(), "predicted_aqi": predicted_aqi})

        next_row = recent_frame.iloc[-1].copy()
        next_row["AQI"] = predicted_aqi
        next_row["Date"] = next_date
        recent_frame = pd.concat([recent_frame, next_row.to_frame().T], ignore_index=True)
        transformed = transform_dataframe(recent_frame.tail(loaded.artifacts.window_size + 1), loaded.artifacts)
        working_window = loaded.artifacts.feature_scaler.transform(transformed[loaded.artifacts.feature_columns].tail(loaded.artifacts.window_size))

    return predictions, working_window
