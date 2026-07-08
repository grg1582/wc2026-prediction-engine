"""CLI: train the Poisson xG model and predict expected goals for a match."""

from __future__ import annotations

import argparse
import sys

from ml.data.ingest import load_results
from ml.elo.calculator import compute_elo_history
from ml.models.poisson import PoissonModel


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="ml.models.run",
        description="Train Poisson xG model and predict expected goals for a match.",
    )
    parser.add_argument(
        "--csv",
        required=True,
        metavar="PATH",
        help="Path to the Kaggle international football results CSV.",
    )
    parser.add_argument(
        "--home",
        required=True,
        metavar="TEAM",
        help="Home team name (exact spelling as in the dataset).",
    )
    parser.add_argument(
        "--away",
        required=True,
        metavar="TEAM",
        help="Away team name (exact spelling as in the dataset).",
    )
    parser.add_argument(
        "--decay",
        type=float,
        default=0.0005,
        metavar="RATE",
        help="Exponential decay rate per day (default: 0.0005, half-life ~3.8 years).",
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

    print("Computing Elo history...")
    df_elo = compute_elo_history(df)

    print(f"Training Poisson xG model (decay_rate={args.decay})...")
    model = PoissonModel()
    try:
        model.fit(df_elo, decay_rate=args.decay)
    except Exception as exc:
        print(f"  Error during training: {exc}", file=sys.stderr)
        sys.exit(1)

    home_coef = model._home_model.coef_
    away_coef = model._away_model.coef_
    print(f"  Home regressor: intercept={model._home_model.intercept_:.4f}, coef={home_coef.tolist()}")
    print(f"  Away regressor: intercept={model._away_model.intercept_:.4f}, coef={away_coef.tolist()}")

    print(f"\nMatch prediction: {args.home} vs {args.away}")
    try:
        home_xg, away_xg = model.predict(args.home, args.away)
    except KeyError as exc:
        print(f"  Error: {exc}", file=sys.stderr)
        sys.exit(1)

    home_elo = model._final_elos[args.home]
    away_elo = model._final_elos[args.away]
    print(f"  {args.home:<30} Elo {home_elo:>7.1f}   xG {home_xg:.2f}")
    print(f"  {args.away:<30} Elo {away_elo:>7.1f}   xG {away_xg:.2f}")


if __name__ == "__main__":
    main()
