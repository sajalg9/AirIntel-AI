from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd
from sklearn.preprocessing import LabelEncoder, StandardScaler

RAW_COLUMNS = ["City", "Date", "AQI", "PM2.5", "PM10", "NO2", "SO2", "CO", "O3"]
POLLUTANT_COLUMNS = ["PM2.5", "PM10", "NO2", "SO2", "CO", "O3"]
DATE_FEATURE_COLUMNS = ["day_of_week", "month", "day_of_year", "is_weekend"]
MODEL_FEATURE_COLUMNS = RAW_COLUMNS[2:] + ["city_encoded"] + DATE_FEATURE_COLUMNS
TARGET_COLUMN = "AQI"


@dataclass
class PreprocessingArtifacts:
    city_encoder: LabelEncoder
    feature_scaler: StandardScaler
    target_scaler: StandardScaler
    feature_columns: list[str]
    window_size: int = 14


def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def discover_csv_files(data_dir: str | Path | None = None) -> list[Path]:
    base_dirs: list[Path] = []
    if data_dir is not None:
        base_dirs.append(Path(data_dir))
    base_dirs.extend([
        project_root(),
        project_root().parent,
        project_root() / "data" / "raw",
    ])

    discovered: list[Path] = []
    seen: set[Path] = set()
    for base_dir in base_dirs:
        if not base_dir.exists():
            continue
        for csv_file in sorted(base_dir.glob("*_AQI_Dataset.csv")):
            resolved = csv_file.resolve()
            if resolved not in seen:
                seen.add(resolved)
                discovered.append(resolved)
    return discovered


def load_all_city_data(data_dir: str | Path | None = None) -> pd.DataFrame:
    csv_files = discover_csv_files(data_dir)
    if not csv_files:
        raise FileNotFoundError("No AQI CSV files found in the workspace.")

    frames = []
    for csv_file in csv_files:
        frame = pd.read_csv(csv_file)
        frame["source_file"] = csv_file.name
        frames.append(frame)

    return pd.concat(frames, ignore_index=True)


def clean_aqi_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    cleaned = df.copy()
    cleaned.columns = [str(column).strip() for column in cleaned.columns]
    cleaned = cleaned.loc[:, ~cleaned.columns.str.contains(r"^Unnamed", case=False, regex=True)]
    cleaned = cleaned.loc[:, [column for column in cleaned.columns if str(column).strip()]]
    cleaned = cleaned.dropna(axis=1, how="all")

    available_columns = [column for column in RAW_COLUMNS if column in cleaned.columns]
    missing_columns = [column for column in RAW_COLUMNS if column not in cleaned.columns]
    if missing_columns:
        raise ValueError(f"Missing expected columns: {missing_columns}")

    cleaned = cleaned[available_columns].copy()
    cleaned["City"] = cleaned["City"].astype(str).str.strip()
    cleaned["Date"] = pd.to_datetime(cleaned["Date"], format="%d/%m/%y", errors="coerce")

    for column in RAW_COLUMNS[2:]:
        cleaned[column] = pd.to_numeric(cleaned[column], errors="coerce")

    cleaned = cleaned.dropna(subset=["City", "Date"])
    cleaned = cleaned.sort_values(["City", "Date"]).reset_index(drop=True)
    return cleaned


def add_date_features(df: pd.DataFrame) -> pd.DataFrame:
    enriched = df.copy()
    enriched["day_of_week"] = enriched["Date"].dt.dayofweek.astype(float)
    enriched["month"] = enriched["Date"].dt.month.astype(float)
    enriched["day_of_year"] = enriched["Date"].dt.dayofyear.astype(float)
    enriched["is_weekend"] = enriched["day_of_week"].isin([5, 6]).astype(float)
    return enriched


def fill_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    filled = df.copy()
    numeric_columns = [column for column in RAW_COLUMNS[2:] + DATE_FEATURE_COLUMNS if column in filled.columns]
    grouped = filled.groupby("City", group_keys=False)
    for column in numeric_columns:
        filled[column] = grouped[column].transform(lambda series: series.interpolate(limit_direction="both").ffill().bfill())
        filled[column] = filled[column].fillna(filled[column].median())
    return filled


def prepare_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    cleaned = clean_aqi_dataframe(df)
    enriched = add_date_features(cleaned)
    enriched = fill_missing_values(enriched)
    enriched["city_encoded"] = 0.0
    return enriched


def fit_preprocessing_artifacts(df: pd.DataFrame, window_size: int = 14) -> PreprocessingArtifacts:
    prepared = prepare_dataframe(df)
    city_encoder = LabelEncoder()
    prepared["city_encoded"] = city_encoder.fit_transform(prepared["City"].astype(str)).astype(float)

    feature_scaler = StandardScaler()
    feature_scaler.fit(prepared[MODEL_FEATURE_COLUMNS])

    target_scaler = StandardScaler()
    target_scaler.fit(prepared[[TARGET_COLUMN]])

    return PreprocessingArtifacts(
        city_encoder=city_encoder,
        feature_scaler=feature_scaler,
        target_scaler=target_scaler,
        feature_columns=MODEL_FEATURE_COLUMNS,
        window_size=window_size,
    )


def transform_dataframe(df: pd.DataFrame, artifacts: PreprocessingArtifacts) -> pd.DataFrame:
    prepared = prepare_dataframe(df)
    prepared["city_encoded"] = artifacts.city_encoder.transform(prepared["City"].astype(str)).astype(float)
    return prepared


def create_time_series_windows(
    df: pd.DataFrame,
    artifacts: PreprocessingArtifacts,
    window_size: int | None = None,
) -> tuple[np.ndarray, np.ndarray, list[pd.Timestamp], list[str]]:
    prepared = transform_dataframe(df, artifacts)
    window_size = window_size or artifacts.window_size

    sequence_windows: list[np.ndarray] = []
    targets: list[float] = []
    target_dates: list[pd.Timestamp] = []
    target_cities: list[str] = []

    for city, city_frame in prepared.groupby("City"):
        city_frame = city_frame.sort_values("Date").reset_index(drop=True)
        if len(city_frame) <= window_size:
            continue

        feature_matrix = artifacts.feature_scaler.transform(city_frame[artifacts.feature_columns])
        target_values = artifacts.target_scaler.transform(city_frame[[TARGET_COLUMN]]).reshape(-1)

        for end_index in range(window_size, len(city_frame)):
            start_index = end_index - window_size
            sequence_windows.append(feature_matrix[start_index:end_index])
            targets.append(target_values[end_index])
            target_dates.append(city_frame.loc[end_index, "Date"])
            target_cities.append(city)

    if not sequence_windows:
        raise ValueError("Not enough data to create time-series windows.")

    return np.asarray(sequence_windows, dtype=np.float32), np.asarray(targets, dtype=np.float32), target_dates, target_cities


def flatten_windows(sequence_windows: np.ndarray) -> np.ndarray:
    return sequence_windows.reshape(sequence_windows.shape[0], -1)


def temporal_train_val_test_split(
    sequence_windows: np.ndarray,
    targets: np.ndarray,
    target_dates: Iterable[pd.Timestamp],
    val_ratio: float = 0.1,
    test_ratio: float = 0.2,
) -> dict[str, tuple[np.ndarray, np.ndarray]]:
    dates = pd.to_datetime(list(target_dates))
    order = np.argsort(dates.to_numpy())
    sequence_windows = sequence_windows[order]
    targets = targets[order]

    total_samples = len(sequence_windows)
    test_size = max(1, int(total_samples * test_ratio))
    val_size = max(1, int(total_samples * val_ratio))
    train_size = max(1, total_samples - test_size - val_size)

    if train_size + val_size + test_size > total_samples:
        overflow = train_size + val_size + test_size - total_samples
        train_size = max(1, train_size - overflow)

    train_end = train_size
    val_end = min(total_samples, train_end + val_size)

    return {
        "train": (sequence_windows[:train_end], targets[:train_end]),
        "val": (sequence_windows[train_end:val_end], targets[train_end:val_end]),
        "test": (sequence_windows[val_end:], targets[val_end:]),
    }


def build_feature_names(window_size: int, feature_columns: list[str]) -> list[str]:
    feature_names: list[str] = []
    for lag in range(window_size, 0, -1):
        for column in feature_columns:
            feature_names.append(f"lag_{lag}_{column}")
    return feature_names


def latest_sequence_for_city(
    df: pd.DataFrame,
    artifacts: PreprocessingArtifacts,
    city: str,
    window_size: int | None = None,
) -> tuple[np.ndarray, pd.DataFrame]:
    prepared = transform_dataframe(df, artifacts)
    city_frame = prepared.loc[prepared["City"].astype(str) == city].sort_values("Date").reset_index(drop=True)
    window_size = window_size or artifacts.window_size
    if len(city_frame) < window_size:
        raise ValueError(f"Not enough history for {city}. Need at least {window_size} rows.")

    feature_matrix = artifacts.feature_scaler.transform(city_frame[artifacts.feature_columns])
    return feature_matrix[-window_size:].astype(np.float32), city_frame.iloc[-window_size:].copy()
