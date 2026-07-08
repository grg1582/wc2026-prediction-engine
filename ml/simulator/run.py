"""CLI: train the Poisson model, then Monte Carlo-simulate the WC2026 knockout
stage from the confirmed quarterfinal bracket."""

from __future__ import annotations

import argparse
import sys

from ml.data.ingest import load_results
from ml.elo.calculator import compute_elo_history
from ml.models.poisson import PoissonModel
from ml.simulator.monte_carlo import simulate_knockout

# Confirmed 2026 quarterfinal bracket (July 9-11, 2026). Semifinal pairing follows
# bracket order: winners of pairs 0 & 1 meet in SF1, winners of pairs 2 & 3 in SF2.
QUARTERFINAL_BRACKET: list[tuple[str, str]] = [
    ("France", "Morocco"),
    ("Spain", "Belgium"),
    ("Norway", "England"),
    ("Argentina", "Switzerland"),
]


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="ml.simulator.run",
        description="Monte Carlo-simulate the World Cup 2026 knockout stage from the quarterfinal.",
    )
    parser.add_argument(
        "--csv",
        required=True,
        metavar="PATH",
        help="Path to the Kaggle international football results CSV.",
    )
    parser.add_argument(
        "--sims",
        type=int,
        default=10_000,
        metavar="N",
        help="Number of Monte Carlo simulations (default: 10,000).",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        metavar="SEED",
        help="Optional RNG seed for reproducible results.",
    )
    parser.add_argument(
        "--decay",
        type=float,
        default=0.0005,
        metavar="RATE",
        help="Poisson model exponential decay rate per day (default: 0.0005).",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    args = _parse_args(argv)

    print(f"Loading results from: {args.csv}")
    df = load_results(args.csv)
    print(
        f"  Loaded {len(df):,} competitive matches "
        f"({df['date'].min().date()} to {df['date'].max().date()})"
    )
    df_elo = compute_elo_history(df)

    print(f"Training Poisson xG model (decay_rate={args.decay})...")
    model = PoissonModel()
    try:
        model.fit(df_elo, decay_rate=args.decay)
    except Exception as exc:
        print(f"  Error during training: {exc}", file=sys.stderr)
        sys.exit(1)

    print(f"Running {args.sims:,} knockout simulations from the quarterfinal...\n")
    try:
        result = simulate_knockout(model, QUARTERFINAL_BRACKET, n_sims=args.sims, seed=args.seed)
    except KeyError as exc:
        print(f"  Error: {exc}", file=sys.stderr)
        sys.exit(1)

    print("Quarterfinals:")
    for qf in result["quarterfinals"]:
        print(
            f"  {qf['home']:<15} (xG {qf['home_xg']:.2f})  {qf['home_win_pct']:>5.1f}%  vs  "
            f"{qf['away_win_pct']:>5.1f}%  ({qf['away_xg']:.2f} xG)  {qf['away']}"
        )

    print("\nTeam advancement probabilities:")
    print(f"  {'Team':<15} {'Reach SF':>9} {'Reach Final':>12} {'Champion':>9} {'3rd Place':>10}")
    ranked = sorted(
        result["team_probabilities"].items(), key=lambda kv: kv[1]["champion"], reverse=True
    )
    for team, p in ranked:
        print(
            f"  {team:<15} {p['reach_semifinal']:>8.1f}% {p['reach_final']:>11.1f}% "
            f"{p['champion']:>8.1f}% {p['third_place']:>9.1f}%"
        )

    print("\nMost likely semifinal matchups:")
    for sf in result["most_likely_semifinals"]:
        print(f"  {' vs '.join(sf['teams']):<30} {sf['probability_pct']:.1f}%")

    print("\nMost likely final matchups:")
    for f in result["most_likely_final"]:
        print(f"  {' vs '.join(f['teams']):<30} {f['probability_pct']:.1f}%")


if __name__ == "__main__":
    main()
