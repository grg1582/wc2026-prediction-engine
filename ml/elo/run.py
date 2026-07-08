"""CLI: compute Elo ratings and print the top N teams. Run from the WC2026/ root."""

from __future__ import annotations

import argparse

from ml.data.ingest import load_results
from ml.elo.calculator import compute_elo


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="ml.elo.run",
        description="Compute Elo ratings for international football teams.",
    )
    parser.add_argument(
        "--csv",
        required=True,
        metavar="PATH",
        help="Path to the Kaggle international football results CSV.",
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--top",
        type=int,
        default=20,
        metavar="N",
        help="Number of top teams to display (default: 20).",
    )
    group.add_argument(
        "--all",
        action="store_true",
        default=False,
        help="Print all rated teams.",
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

    print("Computing Elo ratings...")
    ratings = compute_elo(df)
    total_teams = len(ratings)

    limit = total_teams if args.all else args.top
    subset = list(ratings.items())[:limit]

    header = "All teams" if args.all else f"Top {limit}"
    print(f"\n{header} (out of {total_teams} total):")
    print(f"  {'Rank':<6} {'Team':<35} {'Elo':>8}")
    print(f"  {'-'*6} {'-'*35} {'-'*8}")
    for rank, (team, elo) in enumerate(subset, start=1):
        print(f"  {rank:<6} {team:<35} {elo:>8.1f}")


if __name__ == "__main__":
    main()
