from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

import numpy as np

POLLUTANT_NAMES = {"PM2.5", "PM10", "NO2", "SO2", "CO", "O3"}


@dataclass
class ExplanationResult:
    feature_contributions: list[dict[str, float]]
    pollutant_contributions: list[dict[str, float]]
    raw_values: np.ndarray | None = None


def _aggregate_by_pollutant(shap_values: np.ndarray, feature_names: list[str]) -> list[dict[str, float]]:
    totals: dict[str, float] = {}
    for feature_name, shap_value in zip(feature_names, np.abs(shap_values)):
        match = re.match(r"^lag_\d+_(.+)$", feature_name)
        base_name = match.group(1) if match else feature_name
        if base_name in POLLUTANT_NAMES:
            totals[base_name] = totals.get(base_name, 0.0) + float(shap_value)

    total_value = sum(totals.values()) or 1.0
    ranked = sorted(totals.items(), key=lambda item: item[1], reverse=True)
    return [{"feature": name, "importance": round(value / total_value * 100.0, 2)} for name, value in ranked]


def explain_tree_model(model: Any, input_matrix: np.ndarray, feature_names: list[str], top_k: int = 10) -> ExplanationResult:
    try:
        import shap

        explainer = shap.TreeExplainer(model)
        shap_values = explainer.shap_values(input_matrix)
        if isinstance(shap_values, list):
            shap_values = shap_values[0]
        mean_abs = np.abs(shap_values).mean(axis=0)
        ranked_indices = np.argsort(mean_abs)[::-1][:top_k]
        feature_contributions = [
            {"feature": feature_names[index], "importance": round(float(mean_abs[index]), 6)}
            for index in ranked_indices
        ]
        pollutant_contributions = _aggregate_by_pollutant(shap_values.mean(axis=0), feature_names)
        return ExplanationResult(feature_contributions=feature_contributions, pollutant_contributions=pollutant_contributions, raw_values=np.asarray(shap_values))
    except Exception:
        if hasattr(model, "feature_importances_"):
            importances = np.asarray(model.feature_importances_)
            ranked_indices = np.argsort(importances)[::-1][:top_k]
            feature_contributions = [
                {"feature": feature_names[index], "importance": round(float(importances[index]), 6)}
                for index in ranked_indices
            ]
            pollutant_contributions = _aggregate_by_pollutant(importances, feature_names)
            return ExplanationResult(feature_contributions=feature_contributions, pollutant_contributions=pollutant_contributions)
        fallback_importance = np.ones(len(feature_names), dtype=float)
        pollutant_contributions = _aggregate_by_pollutant(fallback_importance, feature_names)
        return ExplanationResult(feature_contributions=[], pollutant_contributions=pollutant_contributions)
