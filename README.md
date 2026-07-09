# World Cup 2026 Prediction Engine

A monorepo for predicting FIFA World Cup 2026 match outcomes using Elo ratings, Poisson xG modelling, and Monte Carlo simulation.






https://github.com/user-attachments/assets/7514c388-868e-488f-8eaa-6ce65833186e



## Model vs. the market

A sanity check on the quarterfinals: how do this model's odds compare to what
[Polymarket](https://polymarket.com) had priced in for the same four matches?

| Match | This model | Polymarket |
|---|---:|---:|
| France vs. Morocco | France 76.1% · Morocco 23.9% | France 77% · Morocco 23% |
| Spain vs. Belgium | Spain 86.7% · Belgium 13.3% | Spain 74% · Belgium 26% |
| Norway vs. England | Norway 36.7% · England 63.3% | Norway 35% · England 65% |
| Argentina vs. Switzerland | Argentina 85.8% · Switzerland 14.2% | Argentina 74% · Switzerland 26% |

Close on France and Norway/England, with the model notably more confident than
the market on Spain and Argentina. That gap likely runs both ways: the market
can price in news the model never sees (injuries, lineups, current form),
while the model is reading 150+ years of results a bettor might reasonably
weight less heavily against a team's recent stretch.

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
