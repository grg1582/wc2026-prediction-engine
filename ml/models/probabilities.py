"""Converts (home_xg, away_xg) into win/draw/loss probabilities via a double-Poisson
score grid -- the standard score-grid technique from football analytics."""

from __future__ import annotations

import numpy as np
from scipy.stats import poisson


def match_outcome_probabilities(
    home_xg: float, away_xg: float, max_goals: int = 10
) -> tuple[float, float, float]:
    """(p_home_win, p_draw, p_away_win), treating goals as independent Poisson draws."""
    goals = np.arange(max_goals + 1)
    p_home_goals = poisson.pmf(goals, home_xg)
    p_away_goals = poisson.pmf(goals, away_xg)
    grid = np.outer(p_home_goals, p_away_goals)  # grid[h, a] = P(home=h, away=a)

    p_home_win = float(np.tril(grid, k=-1).sum())  # home goals > away goals
    p_draw = float(np.trace(grid))
    p_away_win = float(np.triu(grid, k=1).sum())

    total = p_home_win + p_draw + p_away_win
    return p_home_win / total, p_draw / total, p_away_win / total
