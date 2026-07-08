"""Monte Carlo knockout simulator for the WC2026 bracket, starting from the quarterfinal.

Each match samples home/away goals from independent Poisson draws using the fitted
PoissonModel's expected goals. A regular-time draw is broken with a coin flip weighted
by the Poisson-derived decisive-outcome probability -- standing in for extra time and
penalties without modelling them explicitly. Every round runs vectorised across all
simulations at once, so 10k+ sims of the 8-team bracket finish in well under a second.
"""

from __future__ import annotations

from collections import Counter

import numpy as np

from ml.models.poisson import PoissonModel
from ml.models.probabilities import match_outcome_probabilities


def _pairwise_lambdas(
    model: PoissonModel, teams: list[str]
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    n = len(teams)
    xg_home = np.zeros((n, n))
    xg_away = np.zeros((n, n))
    decisive_home_prob = np.full((n, n), 0.5)

    for i in range(n):
        for j in range(n):
            if i == j:
                continue
            h_xg, a_xg = model.predict(teams[i], teams[j])
            xg_home[i, j] = h_xg
            xg_away[i, j] = a_xg
            p_home, _, p_away = match_outcome_probabilities(h_xg, a_xg)
            decisive_home_prob[i, j] = p_home / (p_home + p_away)

    return xg_home, xg_away, decisive_home_prob


def _simulate_round(
    home_idx: np.ndarray,
    away_idx: np.ndarray,
    xg_home: np.ndarray,
    xg_away: np.ndarray,
    decisive_home_prob: np.ndarray,
    rng: np.random.Generator,
) -> tuple[np.ndarray, np.ndarray]:
    """One round for every match/simulation at once; home_idx/away_idx are (n_matches, n_sims)."""
    lam_home = xg_home[home_idx, away_idx]
    lam_away = xg_away[home_idx, away_idx]
    home_goals = rng.poisson(lam_home)
    away_goals = rng.poisson(lam_away)

    winners = np.where(home_goals > away_goals, home_idx, away_idx)
    draw_mask = home_goals == away_goals
    if draw_mask.any():
        p_home = decisive_home_prob[home_idx[draw_mask], away_idx[draw_mask]]
        coin = rng.random(p_home.shape) < p_home
        winners[draw_mask] = np.where(coin, home_idx[draw_mask], away_idx[draw_mask])

    losers = np.where(winners == home_idx, away_idx, home_idx)
    return winners, losers


def _top_pairings(
    idx_a: np.ndarray, idx_b: np.ndarray, teams: list[str], top_k: int = 3
) -> list[dict]:
    """Most frequent unordered team pairings across simulations."""
    n_sims = idx_a.shape[0]
    counts = Counter(
        tuple(sorted((teams[a], teams[b]))) for a, b in zip(idx_a.tolist(), idx_b.tolist())
    )
    return [
        {"teams": list(pair), "probability_pct": round(100.0 * count / n_sims, 2)}
        for pair, count in counts.most_common(top_k)
    ]


def simulate_knockout(
    model: PoissonModel,
    bracket: list[tuple[str, str]],
    n_sims: int = 10_000,
    seed: int | None = None,
) -> dict:
    """Simulate QF -> SF -> final/3rd-place from a 4-pairing bracket.

    Semifinal pairing follows bracket order: winners of pairs 0 & 1 meet in SF1,
    winners of pairs 2 & 3 meet in SF2.
    """
    if len(bracket) != 4:
        raise ValueError("bracket must contain exactly 4 quarterfinal pairings.")

    teams: list[str] = []
    for home, away in bracket:
        for team in (home, away):
            if team not in teams:
                teams.append(team)
    idx = {team: i for i, team in enumerate(teams)}
    n = len(teams)

    xg_home, xg_away, decisive_home_prob = _pairwise_lambdas(model, teams)
    rng = np.random.default_rng(seed)

    # quarterfinals: fixed matchups, broadcast across all simulations
    qf_home_ids = np.array([idx[home] for home, _ in bracket])
    qf_away_ids = np.array([idx[away] for _, away in bracket])
    qf_home = np.repeat(qf_home_ids[:, None], n_sims, axis=1)
    qf_away = np.repeat(qf_away_ids[:, None], n_sims, axis=1)
    qf_winners, _qf_losers = _simulate_round(
        qf_home, qf_away, xg_home, xg_away, decisive_home_prob, rng
    )

    qf_report = []
    for m, (home, away) in enumerate(bracket):
        home_xg, away_xg = model.predict(home, away)
        home_win_pct = 100.0 * (qf_winners[m] == idx[home]).mean()
        qf_report.append(
            {
                "home": home,
                "away": away,
                "home_xg": round(home_xg, 2),
                "away_xg": round(away_xg, 2),
                "home_win_pct": round(home_win_pct, 2),
                "away_win_pct": round(100.0 - home_win_pct, 2),
            }
        )

    # semifinals: winners of QF0 vs QF1, and QF2 vs QF3
    sf_home = np.stack([qf_winners[0], qf_winners[2]])
    sf_away = np.stack([qf_winners[1], qf_winners[3]])
    sf_winners, sf_losers = _simulate_round(
        sf_home, sf_away, xg_home, xg_away, decisive_home_prob, rng
    )

    # final (SF winners) and third-place playoff (SF losers)
    final_winners, _ = _simulate_round(
        sf_winners[0:1], sf_winners[1:2], xg_home, xg_away, decisive_home_prob, rng
    )
    third_winners, _ = _simulate_round(
        sf_losers[0:1], sf_losers[1:2], xg_home, xg_away, decisive_home_prob, rng
    )

    reach_sf = np.bincount(qf_winners.reshape(-1), minlength=n)
    reach_final = np.bincount(sf_winners.reshape(-1), minlength=n)
    champion = np.bincount(final_winners.reshape(-1), minlength=n)
    third_place = np.bincount(third_winners.reshape(-1), minlength=n)

    team_probabilities = {
        team: {
            "reach_semifinal": round(100.0 * reach_sf[i] / n_sims, 2),
            "reach_final": round(100.0 * reach_final[i] / n_sims, 2),
            "champion": round(100.0 * champion[i] / n_sims, 2),
            "third_place": round(100.0 * third_place[i] / n_sims, 2),
        }
        for team, i in idx.items()
    }

    return {
        "n_simulations": n_sims,
        "quarterfinals": qf_report,
        "team_probabilities": team_probabilities,
        "most_likely_semifinals": [
            _top_pairings(sf_home[0], sf_away[0], teams, top_k=1)[0],
            _top_pairings(sf_home[1], sf_away[1], teams, top_k=1)[0],
        ],
        "most_likely_final": _top_pairings(sf_winners[0], sf_winners[1], teams, top_k=3),
    }
