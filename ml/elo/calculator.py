"""Dynamic Elo rating engine. K=32 for World Cup matches, 20 otherwise; teams start at 1500."""

from __future__ import annotations

import pandas as pd

K_WORLD_CUP: int = 32
K_DEFAULT: int = 20
WORLD_CUP_TOURNAMENT: str = "FIFA World Cup"
INITIAL_ELO: float = 1500.0


def _expected_score(rating_self: float, rating_opp: float) -> float:
    return 1.0 / (1.0 + 10.0 ** ((rating_opp - rating_self) / 400.0))


def _actual_scores(home_score: int, away_score: int) -> tuple[float, float]:
    if home_score > away_score:
        return 1.0, 0.0
    if home_score < away_score:
        return 0.0, 1.0
    return 0.5, 0.5


def compute_elo(df: pd.DataFrame) -> dict[str, float]:
    """Run the chronological Elo update and return final ratings, sorted descending."""
    ratings: dict[str, float] = {}

    for row in df.itertuples(index=False):
        home, away = row.home_team, row.away_team
        ratings.setdefault(home, INITIAL_ELO)
        ratings.setdefault(away, INITIAL_ELO)

        r_home, r_away = ratings[home], ratings[away]
        e_home = _expected_score(r_home, r_away)
        e_away = 1.0 - e_home
        s_home, s_away = _actual_scores(row.home_score, row.away_score)
        k = K_WORLD_CUP if row.tournament == WORLD_CUP_TOURNAMENT else K_DEFAULT

        ratings[home] = r_home + k * (s_home - e_home)
        ratings[away] = r_away + k * (s_away - e_away)

    return dict(sorted(ratings.items(), key=lambda kv: kv[1], reverse=True))


def compute_elo_history(df: pd.DataFrame) -> pd.DataFrame:
    """Same update loop as compute_elo, but records each team's rating before every match."""
    ratings: dict[str, float] = {}
    home_elo_before: list[float] = []
    away_elo_before: list[float] = []

    for row in df.itertuples(index=False):
        home, away = row.home_team, row.away_team
        ratings.setdefault(home, INITIAL_ELO)
        ratings.setdefault(away, INITIAL_ELO)

        r_home, r_away = ratings[home], ratings[away]
        home_elo_before.append(r_home)
        away_elo_before.append(r_away)

        e_home = _expected_score(r_home, r_away)
        e_away = 1.0 - e_home
        s_home, s_away = _actual_scores(row.home_score, row.away_score)
        k = K_WORLD_CUP if row.tournament == WORLD_CUP_TOURNAMENT else K_DEFAULT

        ratings[home] = r_home + k * (s_home - e_home)
        ratings[away] = r_away + k * (s_away - e_away)

    result = df.copy()
    result["home_elo_before"] = home_elo_before
    result["away_elo_before"] = away_elo_before
    return result
