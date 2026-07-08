# api — FastAPI Service

The Poisson model is trained once at startup and cached; requests only run
cheap inference against the cached model.

Endpoints:
- `GET /health` — liveness check
- `GET /rankings?top=20` — current Elo rankings
- `POST /predict/match` — `{home_team, away_team}` → win/draw/loss % and expected goals
- `GET /predict/tournament?sims=10000&seed=42` — Monte Carlo knockout simulation from the quarterfinal

Run from the `WC2026/` root:

```bash
uvicorn api.main:app --reload
```

Requires `data/raw/results.csv` (or set `WC2026_CSV_PATH` to an alternate path).

Async note: `/predict/tournament` is synchronous. That's fine at the current
scope (8-team, 3-round bracket — sub-second even at 10k+ sims). If the
simulator is ever extended to run from the group stage (48 teams, ~1.5M
lookups), revisit with a background task + polling, SSE, or precomputed cache.
