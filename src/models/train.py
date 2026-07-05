from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

try:
    from xgboost import XGBRegressor
except Exception:  # pragma: no cover - optional dependency
    XGBRegressor = None

from ..preprocessing import (
    PreprocessingArtifacts,
    build_feature_names,
    create_time_series_windows,
    discover_csv_files,
    fit_preprocessing_artifacts,
    flatten_windows,
    load_all_city_data,
    temporal_train_val_test_split,
)
from .lstm import train_lstm_model
from .transformer import train_transformer_model


def evaluate_regression(y_true: np.ndarray, y_pred: np.ndarray) -> dict[str, float]:
    mse = mean_squared_error(y_true, y_pred)
    return {
        "mae": float(mean_absolute_error(y_true, y_pred)),
        "rmse": float(np.sqrt(mse)),
        "r2": float(r2_score(y_true, y_pred)),
    }


def fit_tree_models(train_x: np.ndarray, train_y: np.ndarray) -> dict[str, Any]:
    models: dict[str, Any] = {}

    random_forest = RandomForestRegressor(n_estimators=250, max_depth=12, random_state=42, n_jobs=-1)
    random_forest.fit(train_x, train_y)
    models["random_forest"] = random_forest

    if XGBRegressor is not None:
        xgboost = XGBRegressor(
            n_estimators=300,
            learning_rate=0.05,
            max_depth=6,
            subsample=0.85,
            colsample_bytree=0.85,
            objective="reg:squarederror",
            random_state=42,
        )
        xgboost.fit(train_x, train_y)
        models["xgboost"] = xgboost

    return models


def train_all_models(
    data_dir: str | Path | None = None,
    window_size: int = 14,
    output_dir: str | Path | None = None,
    lstm_epochs: int = 20,
    transformer_epochs: int = 20,
) -> dict[str, Any]:
    raw_df = load_all_city_data(data_dir)
    artifacts = fit_preprocessing_artifacts(raw_df, window_size=window_size)
    sequence_windows, targets, target_dates, _ = create_time_series_windows(raw_df, artifacts, window_size=window_size)
    splits = temporal_train_val_test_split(sequence_windows, targets, target_dates)

    train_windows, train_targets = splits["train"]
    val_windows, val_targets = splits["val"]
    test_windows, test_targets = splits["test"]

    train_flat = flatten_windows(train_windows)
    feature_size = train_windows.shape[1] * train_windows.shape[2]
    val_flat = flatten_windows(val_windows) if len(val_windows) else np.empty((0, feature_size), dtype=np.float32)
    test_flat = flatten_windows(test_windows) if len(test_windows) else np.empty((0, feature_size), dtype=np.float32)

    tree_models = fit_tree_models(train_flat, train_targets)
    metrics: dict[str, Any] = {}

    metrics["random_forest"] = evaluate_regression(test_targets, tree_models["random_forest"].predict(test_flat))
    if "xgboost" in tree_models:
        metrics["xgboost"] = evaluate_regression(test_targets, tree_models["xgboost"].predict(test_flat))

    lstm_result = train_lstm_model(
        train_windows,
        train_targets,
        val_windows,
        val_targets,
        input_size=train_windows.shape[-1],
        epochs=lstm_epochs,
    )
    transformer_result = train_transformer_model(
        train_windows,
        train_targets,
        val_windows,
        val_targets,
        input_size=train_windows.shape[-1],
        epochs=transformer_epochs,
    )

    from .lstm import predict_lstm
    from .transformer import predict_transformer

    metrics["lstm"] = evaluate_regression(test_targets, predict_lstm(lstm_result.model, test_windows))
    metrics["transformer"] = evaluate_regression(test_targets, predict_transformer(transformer_result.model, test_windows))

    output_path = Path(output_dir or Path(__file__).resolve().parents[2] / "saved_models")
    output_path.mkdir(parents=True, exist_ok=True)

    joblib.dump(artifacts, output_path / "preprocessing.joblib")
    joblib.dump(tree_models["random_forest"], output_path / "random_forest.joblib")
    if "xgboost" in tree_models:
        joblib.dump(tree_models["xgboost"], output_path / "xgboost.joblib")
    torch_path = output_path / "lstm.pt"
    import torch

    torch.save(lstm_result.model.state_dict(), torch_path)
    torch.save(transformer_result.model.state_dict(), output_path / "transformer.pt")

    training_summary = {
        "window_size": window_size,
        "feature_names": build_feature_names(window_size, artifacts.feature_columns),
        "metrics": metrics,
        "csv_files": [str(path) for path in discover_csv_files(data_dir)],
        "rows": int(len(raw_df)),
        "samples": int(len(sequence_windows)),
    }
    (output_path / "training_metrics.json").write_text(json.dumps(training_summary, indent=2), encoding="utf-8")

    return {
        "artifacts": artifacts,
        "tree_models": tree_models,
        "lstm_model": lstm_result.model,
        "transformer_model": transformer_result.model,
        "metrics": metrics,
        "summary": training_summary,
        "output_dir": output_path,
    }


def main() -> None:
    result = train_all_models()
    print(json.dumps(result["summary"], indent=2, default=str))


if __name__ == "__main__":
    main()
