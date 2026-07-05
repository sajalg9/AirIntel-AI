# AirSense AI

AirSense AI is a smart-city air quality intelligence platform for forecasting AQI, attributing pollution drivers, and generating intervention recommendations for urban decision-makers.

## What is included

- Shared preprocessing pipeline for all five city CSV files
- Baseline machine-learning models: Random Forest and optional XGBoost
- Deep-learning forecasters: PyTorch LSTM and Transformer
- SHAP explainability for pollutant contribution analysis
- Rule-based intervention engine for government and civic action
- Streamlit command-center dashboard

## Project structure

- `data/` - raw city CSVs
- `notebooks/` - EDA and model training notebooks
- `src/` - reusable Python modules
- `app/` - Streamlit dashboard
- `saved_models/` - trained artifacts

## Data notes

The loader searches both the workspace root and `data/raw/` for files named `*_AQI_Dataset.csv`. That means the project works even before the CSVs are moved into the final folder.

## Quick start

1. Create a virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Train the demo models:

```bash
python -m src.models.train
```

4. Launch the dashboard:

```bash
streamlit run app/streamlit_app.py
```

## Notes for the hackathon demo

- The dashboard falls back to a simple history-based forecast if trained artifacts are not yet present.
- The SHAP page uses the tree model when available and automatically falls back to feature-importance style explanations if SHAP cannot be loaded.
- The intervention engine is intentionally rule-driven so the advisory layer remains deterministic and easy to explain in a demo.
