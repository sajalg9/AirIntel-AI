🌫️ AirIntel AI — Urban Air Quality Intelligence Platform

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white"/>
  <img src="https://img.shields.io/badge/FastAPI-Backend-009688?style=for-the-badge&logo=fastapi&logoColor=white"/>
  <img src="https://img.shields.io/badge/React-Frontend-61DAFB?style=for-the-badge&logo=react&logoColor=black"/>
  <img src="https://img.shields.io/badge/Scikit--Learn-ML-F7931E?style=for-the-badge&logo=scikitlearn&logoColor=white"/>
  <img src="https://img.shields.io/badge/PyTorch-Deep%20Learning-EE4C2C?style=for-the-badge&logo=pytorch&logoColor=white"/>
  <img src="https://img.shields.io/badge/Vercel-Deployed-000000?style=for-the-badge&logo=vercel&logoColor=white"/>
</p>
<p align="center">
  <b>ET AI Hackathon 2.0 · Problem Statement 5 · Smart Cities / Environmental Intelligence</b>
</p>

🔗 Live Links

Link🌐 Live Applicationhttps://air-intel-ai.vercel.app⚙️ API Documentationhttps://airintel-backend.onrender.com/docs📦 Backend Healthhttps://airintel-backend.onrender.com/health


📌 Problem Statement

India's air quality crisis is not a Delhi problem — it is a national urban crisis. Despite over 900 CAAQMS monitoring stations deployed under the National Clean Air Programme, a 2024 CAG audit found only 31% of cities with monitoring data had any actionable multi-agency response linked to those readings.

The data exists. The intelligence layer to act on it does not.

City administrations need:


Predictive forecasting — what will AQI be in 24–72 hours?
Source attribution — which pollutant is responsible, right now?
Enforcement intelligence — where to deploy action for maximum impact?
Citizen advisories — in regional languages, not just English


AirIntel AI addresses all four.


✨ What It Does

⚡ Command Center

Real-time AQI dashboard for any Indian city. Shows current AQI, 24/48/72hr forecast cards, pollutant breakdown (PM2.5, PM10, NO₂, SO₂, CO, O₃) with percentage contribution bars, and 4-point trend summary.

📈 AQI Forecast

Full historical chart (2018–2024) with interactive time scrubber + multi-model forward prediction overlay. Toggle between LSTM, Transformer, and Random Forest predictions on the same chart. Forecast summary cards at the bottom colour-coded by AQI severity.

🏙️ City Comparison

Multi-select grouped bar chart comparing current + 3-day forecast AQI across Delhi, Mumbai, Bangalore, Hyderabad, and Chennai simultaneously. Sortable summary table with severity badges.

🔍 Source Attribution

Pollutant contribution analysis using SHAP (SHapley Additive exPlanations) over the Random Forest model. Per-city breakdown showing which pollutant drives the AQI for that specific city's latest readings, not a global average.

🩺 Health Advisory

AI-generated intervention plan combining predicted AQI + dominant pollutant data with the recommendation agent. Outputs risk level, health advisory text, prioritised government interventions, and a multilingual citizen alert in the city's native language:

CityLanguageDelhiHindiMumbaiMarathiBangaloreKannadaChennaiTamilHyderabadTelugu


🧠 ML Pipeline

Raw CPCB AQI Data (5 cities, 2018–2024)
              ↓
  Data Cleaning + Date Parsing
              ↓
  Feature Engineering
  (AQI, PM2.5, PM10, NO₂, SO₂, CO, O₃,
   city_encoded, day_of_week, month,
   day_of_year, is_weekend — 12 features)
              ↓
  14-day Sliding Window → 11,972 samples
              ↓
  Temporal Train / Val / Test Split
  (70% / 10% / 20%)
              ↓
  ┌─────────────┬──────────────┬──────────┬─────────────┐
  │Random Forest│   XGBoost    │   LSTM   │ Transformer │
  └─────────────┴──────────────┴──────────┴─────────────┘
              ↓
  Iterative 72-hour Forward Forecast
  (autoregressive: each prediction feeds next window)
              ↓
  SHAP Explainability → Source Attribution
              ↓
  Recommendation Agent → Advisory + Interventions

Model Performance (scaled AQI, StandardScaler)

ModelR²MAERMSERandom Forest0.92150.1930.303XGBoost0.91700.1960.312Transformer0.91550.1980.315LSTM0.91280.2060.319

Random Forest is the primary inference model. LSTM and Transformer weights are saved for future use.


🏗️ System Architecture

┌─────────────────────────────────────────┐
│           React Frontend (Vercel)        │
│  Command Center │ Forecast │ Compare     │
│  Explain        │ Advisory               │
└──────────────────┬──────────────────────┘
                   │  REST API (HTTPS)
                   ▼
┌─────────────────────────────────────────┐
│        FastAPI Backend (Render)          │
│                                          │
│  /api/current/{city}                     │
│  /api/forecast      POST                 │
│  /api/compare       GET                  │
│  /api/explain/{city}                     │
│  /api/advisory      POST                 │
│  /health            GET                  │
│                                          │
│  ┌──────────────────────────────────┐    │
│  │       src/ (Copilot-assisted)    │    │
│  │  preprocessing.py                │    │
│  │  models/ (lstm, transformer)     │    │
│  │  agents/recommendation_agent.py  │    │
│  │  explainability/shap_analysis.py │    │
│  └──────────────────────────────────┘    │
│                                          │
│  data/raw/  ← 5 city CSV files           │
│  saved_models/  ← trained weights        │
└─────────────────────────────────────────┘


🛠️ Tech Stack

Frontend


React 18 + Vite
Tailwind CSS
Recharts (all charts)
React Router v6
Axios


Backend


FastAPI + Uvicorn
Pandas + NumPy
Scikit-learn (Random Forest, preprocessing)
XGBoost
PyTorch (LSTM, Transformer)
SHAP
Joblib
Pydantic v2


Deployment


Frontend → Vercel
Backend API → Render (free tier)



📡 API Reference

EndpointMethodInputDescription/api/citiesGET—List of available cities/api/current/{city}GETcity nameLatest AQI + pollutant breakdown/api/forecastPOST{city, days_ahead, model}Historical + N-day forecast/api/compareGET?cities=Delhi,Mumbai,...Multi-city current + forecast/api/explain/{city}GETcity namePollutant % contribution/api/advisoryPOST{city, model}Risk level + interventions/healthGET—Server status


📂 Project Structure

AirIntel-AI/
│
├── app/
│   ├── backend/
│   │   └── main.py              ← FastAPI app, all endpoints
│   └── frontend/
│       ├── src/
│       │   ├── components/
│       │   │   └── AQIUtils.jsx ← Shared cards, colours, selectors
│       │   └── pages/
│       │       ├── Home.jsx     ← Command Center
│       │       ├── Forecast.jsx ← Chart + time scrubber
│       │       ├── Compare.jsx  ← Multi-city bar chart
│       │       ├── Explain.jsx  ← SHAP attribution
│       │       └── Advisory.jsx ← Health + Indic advisory
│       ├── package.json
│       └── vite.config.js
│
├── src/
│   ├── preprocessing.py         ← Data loading, feature engineering, windows
│   ├── models/
│   │   ├── lstm.py              ← PyTorch LSTM
│   │   └── transformer.py       ← PyTorch Transformer
│   ├── agents/
│   │   └── recommendation_agent.py ← Intervention generator
│   └── explainability/
│       └── shap_analysis.py     ← SHAP over Random Forest
│
├── data/
│   └── raw/                     ← 5 city CPCB AQI CSVs (2018–2024)
│
├── saved_models/                ← Trained model weights + preprocessing artifacts
│   ├── random_forest.joblib
│   ├── xgboost.joblib
│   ├── lstm.pt
│   ├── transformer.pt
│   └── preprocessing.joblib
│
├── notebooks/
│   ├── EDA.ipynb
│   ├── model_training.ipynb
│   └── AirSense_Runbook.ipynb
│
├── requirements.txt
└── README.md


🚀 Running Locally

1. Clone

bashgit clone https://github.com/sajalg9/AirIntel-AI.git
cd AirIntel-AI

2. Backend

bashpython -m venv .venv
.venv\Scripts\activate        # Windows
source .venv/bin/activate     # Mac/Linux

pip install -r requirements.txt

uvicorn app.backend.main:app --reload --port 8000

Backend runs at http://localhost:8000
API docs at http://localhost:8000/docs

3. Frontend

bashcd app/frontend
npm install
npm run dev

Frontend runs at http://localhost:3000


Make sure backend is running first. Vite proxies /api to localhost:8000 automatically.




📊 Dataset

PropertyDetailSourceCPCB (Central Pollution Control Board) via cp099/India-Air-Quality-DatasetCitiesDelhi, Mumbai, Bangalore, Hyderabad, ChennaiPeriodJanuary 2018 – December 2024FrequencyDaily averagesTotal rows12,042FeaturesAQI, PM2.5, PM10, NO₂, SO₂, CO, O₃

Note on data currency: The models learn seasonal and meteorological patterns (monsoon cycles, winter inversions, traffic-pollution correlations) that are physically stable year to year. In production, the /api/current/{city} endpoint would pull from the OpenAQ live API with zero pipeline changes.


🌍 Roadmap


 Live CPCB / OpenAQ API integration
 Satellite AOD data (Sentinel-5P) for source attribution
 Ward-level hyperlocal forecasting
 ConvLSTM spatio-temporal model across city grid
 Mobile app (React Native)
 More cities (Kolkata, Pune, Ahmedabad, Lucknow)



👨‍💻 Built By

Sajal Goel
B.Tech Computer Science Engineering, Punjab Engineering College (PEC), Chandigarh
GitHub: @sajalg9

Built for ET AI Hackathon 2.0 — Problem Statement 5: Urban Air Quality Intelligence


<p align="center">
  <b>🌱 AI for cleaner cities</b>
</p>
