"""FastAPI service: Elo rankings, single-match predictions, knockout tournament sims.

The Poisson model trains once at startup and is cached; requests just run cheap
inference against it. That's why /predict/tournament can stay a plain sync def --
at 8 teams/3 rounds, 10k sims finish in well under a second. Revisit if this ever
grows to a full 48-team group-stage simulation.

Run from the WC2026/ root: uvicorn api.main:app --reload
"""

from __future__ import annotations

import os
from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncIterator

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from ml.data.ingest import load_results
from ml.elo.calculator import compute_elo, compute_elo_history
from ml.models.poisson import PoissonModel
from ml.models.probabilities import match_outcome_probabilities
from ml.simulator.monte_carlo import simulate_knockout
from ml.simulator.run import QUARTERFINAL_BRACKET

CSV_PATH = Path(os.environ.get("WC2026_CSV_PATH", "data/raw/results.csv"))

# Origins for local frontend dev servers (Vite default + common alternates).
ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]


class _ModelCache:
    elo_ratings: dict[str, float]
    poisson_model: PoissonModel


model_cache = _ModelCache()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    if not CSV_PATH.exists():
        raise FileNotFoundError(
            f"Results CSV not found at '{CSV_PATH}'. Download the Kaggle martj42 "
            "dataset to data/raw/results.csv, or set WC2026_CSV_PATH."
        )
    df = load_results(CSV_PATH)
    df_elo = compute_elo_history(df)
    model_cache.elo_ratings = compute_elo(df)
    model_cache.poisson_model = PoissonModel().fit(df_elo)
    yield


app = FastAPI(title="WC2026 Prediction API", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


class MatchRequest(BaseModel):
    home_team: str
    away_team: str


class MatchResponse(BaseModel):
    home_team: str
    away_team: str
    home_elo: float
    away_elo: float
    home_xg: float
    away_xg: float
    home_win_pct: float
    draw_pct: float
    away_win_pct: float


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/rankings")
def rankings(top: int = 20) -> list[dict]:
    """Current Elo rankings, highest first."""
    items = list(model_cache.elo_ratings.items())[:top]
    return [{"rank": i + 1, "team": team, "elo": round(elo, 1)} for i, (team, elo) in enumerate(items)]


@app.post("/predict/match", response_model=MatchResponse)
def predict_match(request: MatchRequest) -> MatchResponse:
    """Win / draw / loss probabilities and expected goals for a single match."""
    model = model_cache.poisson_model
    try:
        home_xg, away_xg = model.predict(request.home_team, request.away_team)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    home_win_pct, draw_pct, away_win_pct = match_outcome_probabilities(home_xg, away_xg)

    return MatchResponse(
        home_team=request.home_team,
        away_team=request.away_team,
        home_elo=round(model_cache.elo_ratings[request.home_team], 1),
        away_elo=round(model_cache.elo_ratings[request.away_team], 1),
        home_xg=round(home_xg, 2),
        away_xg=round(away_xg, 2),
        home_win_pct=round(100 * home_win_pct, 2),
        draw_pct=round(100 * draw_pct, 2),
        away_win_pct=round(100 * away_win_pct, 2),
    )


@app.get("/predict/tournament")
def predict_tournament(sims: int = 10_000, seed: int | None = None) -> dict:
    """Monte Carlo simulation of the knockout stage from the quarterfinal."""
    if not 100 <= sims <= 200_000:
        raise HTTPException(status_code=400, detail="sims must be between 100 and 200,000.")
    return simulate_knockout(model_cache.poisson_model, QUARTERFINAL_BRACKET, n_sims=sims, seed=seed)
