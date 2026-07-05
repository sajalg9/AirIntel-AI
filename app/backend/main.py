"""
AirIntel AI — FastAPI Backend
Exposes AQI forecast, explanation, and advisory endpoints.
Imports from src/ — no model logic duplicated here.
Run: uvicorn app.backend.main:app --reload --port 8000
"""
from __future__ import annotations

import sys
import os
from pathlib import Path
import uvicorn

# ── path setup ──────────────────────────────────────────────────────────────
ROOT = Path(__file__).resolve().parents[2]   # AirSense-AI/
sys.path.insert(0, str(ROOT))

import joblib
import numpy as np
import pandas as pd
import torch
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from src.preprocessing import (
    load_all_city_data,
    fit_preprocessing_artifacts,
    latest_sequence_for_city,
    flatten_windows,
    PreprocessingArtifacts,
)
from src.agents.recommendation_agent import generate_recommendations
from src.models.lstm import AQILSTMRegressor, predict_lstm

# ── app setup ────────────────────────────────────────────────────────────────
app = FastAPI(title="AirIntel AI", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

CITIES = ["Delhi", "Mumbai", "Bangalore", "Hyderabad", "Chennai"]
MODELS_DIR = ROOT / "saved_models"
DATA_DIR   = ROOT / "data" / "raw"

# ── load artifacts at startup ─────────────────────────────────────────────────
@app.on_event("startup")
def load_artifacts():
    global df_all, artifacts, rf_model, xgb_model, lstm_model, transformer_model

    # Raw data
    df_all = load_all_city_data(DATA_DIR)

    # Preprocessing artifacts
    artifacts = joblib.load(MODELS_DIR / "preprocessing.joblib")

    # Sklearn models
    rf_model  = joblib.load(MODELS_DIR / "random_forest.joblib")
    xgb_model = joblib.load(MODELS_DIR / "xgboost.joblib")

    # PyTorch LSTM
    input_size  = len(artifacts.feature_columns)
    lstm_model  = AQILSTMRegressor(input_size=input_size, hidden_size=64, num_layers=2)
    lstm_model.load_state_dict(torch.load(MODELS_DIR / "lstm.pt", map_location="cpu"))
    lstm_model.eval()

    # PyTorch Transformer (same interface as LSTM via predict_lstm)
    from src.models.transformer import AQITransformerRegressor
    transformer_model = AQITransformerRegressor(input_size=input_size)
    transformer_model.load_state_dict(
        torch.load(MODELS_DIR / "transformer.pt", map_location="cpu")
    )
    transformer_model.eval()

    print("✅ Models loaded.")


# ── helpers ───────────────────────────────────────────────────────────────────
def _predict_aqi(city: str, model_name: str = "random_forest") -> float:
    """Return denormalised AQI prediction for city using chosen model."""
    window_2d, _ = latest_sequence_for_city(df_all, artifacts, city)
    window_3d    = window_2d[np.newaxis, :, :]   # (1, 14, 12)
    flat         = flatten_windows(window_3d)     # (1, 168)

    if model_name == "random_forest":
        scaled = rf_model.predict(flat)
    elif model_name == "xgboost":
        scaled = xgb_model.predict(flat)
    elif model_name == "lstm":
        scaled = predict_lstm(lstm_model, window_3d)
    elif model_name == "transformer":
        scaled = predict_lstm(transformer_model, window_3d)
    else:
        raise ValueError(f"Unknown model: {model_name}")

    aqi = float(artifacts.target_scaler.inverse_transform([[scaled[0]]])[0][0])
    return round(aqi, 1)


def _iterative_forecast(city: str, days: int, model_name: str = "lstm") -> list[float]:
    """
    Multi-step forecast: predict day+1, slide window, predict day+2, etc.
    Non-AQI features are held constant at their last known values.
    """
    window_2d, _ = latest_sequence_for_city(df_all, artifacts, city)
    window = window_2d.copy()   # (14, 12)
    aqi_col = artifacts.feature_columns.index("AQI")
    preds   = []

    for _ in range(days):
        w3d   = window[np.newaxis, :, :]
        flat  = flatten_windows(w3d)

        if model_name in ("lstm", "transformer"):
            mdl   = lstm_model if model_name == "lstm" else transformer_model
            scaled = predict_lstm(mdl, w3d)[0]
        else:
            scaled = rf_model.predict(flat)[0]

        aqi_raw = float(artifacts.target_scaler.inverse_transform([[scaled]])[0][0])
        preds.append(round(aqi_raw, 1))

        # Slide: drop oldest row, append copy of last row with predicted AQI
        new_row           = window[-1].copy()
        new_row[aqi_col]  = float(scaled)   # replace AQI with predicted (scaled)
        window            = np.vstack([window[1:], new_row[np.newaxis, :]])

    return preds


def _get_latest_row(city: str) -> dict:
    city_df = df_all[df_all["City"] == city].sort_values("Date")
    if city_df.empty:
        raise HTTPException(404, f"No data for {city}")
    row = city_df.iloc[-1]
    return {
        "date":   str(pd.Timestamp(row["Date"]).date()),
        "AQI":    round(float(row["AQI"]), 1),
        "PM2.5":  round(float(row["PM2.5"]), 1),
        "PM10":   round(float(row["PM10"]), 1),
        "NO2":    round(float(row["NO2"]), 1),
        "SO2":    round(float(row["SO2"]), 1),
        "CO":     round(float(row["CO"]), 3),
        "O3":     round(float(row["O3"]), 1),
    }


def _aqi_category(aqi: float) -> str:
    for cap, cat in [(50,"Good"),(100,"Satisfactory"),(200,"Moderate"),
                     (300,"Poor"),(400,"Very Poor"),(float("inf"),"Severe")]:
        if aqi <= cap:
            return cat
    return "Severe"


# ── Pydantic models ───────────────────────────────────────────────────────────
class ForecastRequest(BaseModel):
    city: str
    days_ahead: int = 3
    model: str = "lstm"   # lstm | transformer | random_forest

class AdvisoryRequest(BaseModel):
    city: str
    model: str = "random_forest"


# ── Endpoints ─────────────────────────────────────────────────────────────────

@app.get("/api/cities")
def get_cities():
    """List of available cities."""
    return {"cities": CITIES}


@app.get("/api/current/{city}")
def get_current(city: str):
    """Latest observed AQI + pollutant breakdown for a city."""
    if city not in CITIES:
        raise HTTPException(404, f"City '{city}' not found.")
    row = _get_latest_row(city)
    row["category"] = _aqi_category(row["AQI"])
    pollutants = {k: row[k] for k in ["PM2.5","PM10","NO2","SO2","CO","O3"]}
    total = sum(pollutants.values()) or 1
    row["pollutant_pct"] = {k: round(v/total*100, 1) for k,v in pollutants.items()}
    return row


@app.post("/api/forecast")
def post_forecast(req: ForecastRequest):
    """Iterative AQI forecast for N days ahead."""
    if req.city not in CITIES:
        raise HTTPException(404, f"City '{req.city}' not found.")
    if not 1 <= req.days_ahead <= 14:
        raise HTTPException(400, "days_ahead must be 1–14.")

    preds = _iterative_forecast(req.city, req.days_ahead, req.model)
    # Also grab last 30 days of historical AQI for chart context
    city_df = df_all[df_all["City"] == req.city].copy()
    city_df["Date"] = pd.to_datetime(city_df["Date"])
    city_df = city_df.sort_values("Date")
    historical = [
        {"date": str(pd.Timestamp(r["Date"]).date()), "aqi": round(float(r["AQI"]), 1)}
        for _, r in city_df.iterrows()
    ]
    return {
        "city":       req.city,
        "model":      req.model,
        "historical": historical,
        "forecast":   [
            {"day": i+1, "predicted_aqi": v, "category": _aqi_category(v)}
            for i, v in enumerate(preds)
        ],
    }


@app.get("/api/compare")
def get_compare(cities: str = Query(..., description="Comma-separated city names")):
    """Current + 3-day forecast AQI for multiple cities."""
    city_list = [c.strip() for c in cities.split(",")]
    invalid   = [c for c in city_list if c not in CITIES]
    if invalid:
        raise HTTPException(404, f"Unknown cities: {invalid}")

    result = []
    for city in city_list:
        row   = _get_latest_row(city)
        preds = _iterative_forecast(city, 3, "random_forest")
        result.append({
            "city":          city,
            "current_aqi":   row["AQI"],
            "category":      _aqi_category(row["AQI"]),
            "forecast_day1": preds[0],
            "forecast_day2": preds[1],
            "forecast_day3": preds[2],
        })
    return {"comparison": result}


@app.get("/api/explain/{city}")
def get_explain(city: str):
    if city not in CITIES:
        raise HTTPException(404, f"City '{city}' not found.")

    from src.explainability.shap_analysis import explain_tree_model
    import json

    # Get THIS city's latest 14-day window only
    window_2d, _ = latest_sequence_for_city(df_all, artifacts, city)
    flat = flatten_windows(window_2d[np.newaxis, :, :])  # (1, 168)

    feature_names = artifacts.feature_columns  # 12 base features
    # Build lagged feature names matching training (lag_14_AQI, lag_13_AQI, ...)
    from src.preprocessing import build_feature_names
    lag_names = build_feature_names(artifacts.window_size, feature_names)

    result = explain_tree_model(rf_model, flat, lag_names)

    # pollutant_contributions is already per-city since we passed only city's window
    contributions = {
        d["feature"]: d["importance"]
        for d in result.pollutant_contributions
    }
    dominant = max(contributions, key=contributions.get)

    return {
        "city":          city,
        "contributions": contributions,
        "dominant":      dominant,
        "summary":       f"{dominant} is the dominant driver at {contributions[dominant]:.1f}%.",
    }

@app.post("/api/advisory")
def post_advisory(req: AdvisoryRequest):
    """Full health advisory + intervention plan for a city."""
    if req.city not in CITIES:
        raise HTTPException(404, f"City '{req.city}' not found.")

    predicted_aqi = _predict_aqi(req.city, req.model)
    row           = _get_latest_row(req.city)
    pols          = {k: row[k] for k in ["PM2.5","PM10","NO2","SO2","CO","O3"]}
    total         = sum(pols.values()) or 1
    dominant      = sorted(pols.items(), key=lambda x:-x[1])[:3]
    dominant_pct  = [(k, round(v/total*100, 1)) for k,v in dominant]

    plan = generate_recommendations(req.city, predicted_aqi, dominant_pct)
    return {
        "city":             plan.city,
        "predicted_aqi":    round(plan.predicted_aqi, 1),
        "category":         plan.category,
        "risk_level":       plan.risk_level,
        "health_advisory":  plan.health_advisory,
        "interventions":    plan.interventions,
    }


@app.get("/health")
def health():
    return {"status": "ok", "models_loaded": True}


if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run("app.backend.main:app", host="0.0.0.0", port=port, reload=False)
