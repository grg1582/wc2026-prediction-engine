# ml/elo — Elo Rating Engine

Dynamic Elo system processing all competitive international matches chronologically.

- K=32 for FIFA World Cup matches
- K=20 for all other competitive matches
- All teams start at 1500; no pre-seeding
- Outputs `{team: elo}` sorted descending

Run via: `python -m ml.elo.run --csv data/raw/results.csv`
