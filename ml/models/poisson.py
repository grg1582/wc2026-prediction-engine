"""Poisson xG model: two independent Poisson regressors (home/away goals) on pre-match
Elo, with exponential time-decay weights so old, high-scoring eras don't skew today's predictions."""

from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.linear_model import PoissonRegressor

from ml.elo.calculator import compute_elo


class PoissonModel:
    def __init__(self) -> None:
        self._home_model: PoissonRegressor | None = None
        self._away_model: PoissonRegressor | None = None
        self._final_elos: dict[str, float] = {}
        self._decay_rate: float = 0.0

    def fit(self, df: pd.DataFrame, decay_rate: float = 0.0005) -> "PoissonModel":
        # default rate -> ~3.8yr half-life, keeps the pre-1990s high-scoring era
        # from distorting modern predictions
        reference_date = df["date"].max()
        days_ago = (reference_date - df["date"]).dt.days.astype(float)
        weights = np.exp(-decay_rate * days_ago)

        X = df[["home_elo_before", "away_elo_before"]].to_numpy()
        y_home = df["home_score"].to_numpy()
        y_away = df["away_score"].to_numpy()

        self._home_model = PoissonRegressor(alpha=0, max_iter=300)
        self._away_model = PoissonRegressor(alpha=0, max_iter=300)
        self._home_model.fit(X, y_home, sample_weight=weights)
        self._away_model.fit(X, y_away, sample_weight=weights)

        self._decay_rate = decay_rate
        self._final_elos = compute_elo(df)
        return self

    def predict(self, home_team: str, away_team: str) -> tuple[float, float]:
        """Expected goals (home_xg, away_xg) for a matchup."""
        if self._home_model is None:
            raise ValueError("Model has not been fitted. Call fit() first.")

        for team in (home_team, away_team):
            if team not in self._final_elos:
                raise KeyError(f"Team '{team}' not found in training data.")

        X_pred = np.array([[self._final_elos[home_team], self._final_elos[away_team]]])
        home_xg = float(self._home_model.predict(X_pred)[0])
        away_xg = float(self._away_model.predict(X_pred)[0])
        return home_xg, away_xg
