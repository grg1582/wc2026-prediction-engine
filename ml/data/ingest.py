"""Loads and cleans the Kaggle martj42 international football results CSV."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

# Exclusion list, not inclusion: new tournament names should default to competitive.
NON_COMPETITIVE: frozenset[str] = frozenset({"Friendly"})


def load_results(csv_path: str | Path) -> pd.DataFrame:
    """Load, clean and filter to competitive matches, sorted by date ascending."""
    csv_path = Path(csv_path)
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV not found: {csv_path}")

    df = pd.read_csv(
        csv_path,
        dtype={"home_team": str, "away_team": str, "tournament": str},
    )

    df["date"] = pd.to_datetime(df["date"], format="%Y-%m-%d", errors="coerce")

    core_cols = ["date", "home_team", "away_team", "home_score", "away_score", "tournament"]
    df = df.dropna(subset=core_cols).copy()

    # some historical rows have non-integer scores
    df["home_score"] = pd.to_numeric(df["home_score"], errors="coerce")
    df["away_score"] = pd.to_numeric(df["away_score"], errors="coerce")
    df = df.dropna(subset=["home_score", "away_score"])
    df["home_score"] = df["home_score"].astype(int)
    df["away_score"] = df["away_score"].astype(int)

    df = df[~df["tournament"].isin(NON_COMPETITIVE)].copy()
    df = df.sort_values("date", ascending=True).reset_index(drop=True)

    return df[["date", "home_team", "away_team", "home_score", "away_score", "tournament"]]
