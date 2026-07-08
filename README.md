# World Cup 2026 Prediction Engine

A monorepo for predicting FIFA World Cup 2026 match outcomes using Elo ratings, Poisson xG modelling, and Monte Carlo simulation.




https://github.com/user-attachments/assets/dd91fd96-8ebc-4b83-adce-a6fb9e26a13d



## Structure

- `ml/` — Machine-learning pipeline: data ingestion, Elo ratings, Poisson model, Monte Carlo simulator
- `api/` — FastAPI service exposing prediction endpoints
- `frontend/` — React + TypeScript dashboard

## Quick Start

```bash
pip install -r requirements.txt

# Download the Kaggle martj42 results CSV and place it at data/raw/results.csv
python -m ml.elo.run --csv data/raw/results.csv

# Monte Carlo-simulate the knockout stage from the quarterfinal
python -m ml.simulator.run --csv data/raw/results.csv

# API + frontend (two terminals, from their respective directories)
uvicorn api.main:app --reload
cd frontend && npm install && npm run dev
```
