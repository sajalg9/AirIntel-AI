# 🌫️ AirIntel AI — Urban Air Quality Intelligence System

![Python](https://img.shields.io/badge/Python-3.11-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-green)
![React](https://img.shields.io/badge/React-Frontend-blue)
![Machine%20Learning](https://img.shields.io/badge/AI-ML%20Forecasting-orange)
![Deployment](https://img.shields.io/badge/Deployment-Vercel%20%2B%20Render-purple)

## 🚀 Live Demo

🌐 **Application:**  
https://air-intel-ai.vercel.app

⚙️ **API Documentation:**  
https://airintel-backend.onrender.com/docs


---

# 📌 Overview

**AirIntel AI** is an intelligent urban air-quality analytics platform that predicts, explains, and provides actionable insights about air pollution trends across major Indian cities.

The system combines:

- 🤖 Machine Learning based AQI forecasting
- 📊 Real-time air quality dashboards
- 🔍 Pollutant source attribution
- 🏙️ Multi-city comparison
- 🩺 Health advisory generation

Designed as an AI-powered decision support system for citizens, researchers, and urban planners.


---

# ✨ Features

## ⚡ Command Center

A real-time AQI intelligence dashboard.

- Current AQI monitoring
- Pollutant breakdown
- AQI category detection
- City-wise environmental insights


---

## 📈 AQI Forecasting

Predicts future AQI trends using machine learning pipelines.

Features:

- Multi-day AQI forecasting
- Historical AQI visualization
- Trend analysis
- Pollution category prediction


---

## 🏙️ City Comparison

Compare pollution levels across:

- Delhi
- Mumbai
- Bangalore
- Hyderabad
- Chennai

Includes:

- Current AQI comparison
- Future AQI trends
- Pollution severity ranking


---

## 🔍 Source Attribution

Identifies dominant pollution contributors.

Analyzes:

- PM2.5
- PM10
- NO₂
- SO₂
- CO
- O₃

Provides percentage-based pollutant contribution insights.


---

## 🩺 Health Advisory Agent

Generates pollution-aware recommendations:

- Risk assessment based on AQI severity
- Health warnings and safety guidance
- Preventive measures for citizens
- Pollution control suggestions
- Multilingual Indic alerts (Hindi, Marathi, Kannada, Tamil, Telugu)


---

# 🧠 AI / ML Pipeline

AirIntel AI uses a complete machine-learning workflow:

```
Raw AQI Dataset
        ↓
Data Cleaning
        ↓
Feature Engineering
        ↓
Time-Series Window Creation
        ↓
ML Forecasting Models
        ↓
AQI Prediction
        ↓
Insights + Recommendations
```

Models experimented:

- Random Forest
- LSTM
- Transformer-based forecasting


---

# 🏗️ System Architecture


```
                 React Frontend
                      |
                      |
                 REST API Calls
                      |
                      ↓
              FastAPI Backend
                      |
        -------------------------
        |                       |
 AQI Forecast Engine    Advisory Agent
        |
 Machine Learning Pipeline
        |
 Pollution Dataset
```


---

# 🛠️ Tech Stack


## Frontend

- React.js
- Vite
- Recharts
- Axios
- Tailwind CSS


## Backend

- FastAPI
- Python
- Uvicorn
- Pydantic


## Machine Learning

- Scikit-learn
- Pandas
- NumPy
- Joblib
- Deep Learning experiments


## Deployment

- Frontend → Vercel
- Backend API → Render


---

# 📡 API Endpoints


| Endpoint | Method | Description |
|-|-|-|
| `/api/current/{city}` | GET | Current AQI details |
| `/api/forecast` | POST | AQI prediction |
| `/api/compare` | GET | Compare multiple cities |
| `/api/explain/{city}` | GET | Pollutant attribution |
| `/api/advisory` | POST | Health recommendations |
| `/health` | GET | Server status |


---

# 📂 Project Structure


```
AirIntel-AI/

├── app/
│   ├── backend/
│   │   └── main.py
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   └── lib/
│
├── src/
│   ├── models/
│   ├── preprocessing.py
│   └── agents/
│
├── data/
│   └── raw/
│
├── saved_models/
│
└── README.md
```

---

# 🌍 Future Improvements

- Live government AQI API integration
- More cities coverage
- Satellite pollution data
- Advanced Transformer forecasting
- Mobile application



