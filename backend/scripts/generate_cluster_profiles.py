"""Generate original-unit profiles for selected K-Means candidates."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

import pandas as pd


BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.services.cluster_profiling import (  # noqa: E402
    BEHAVIORAL_FEATURES,
    profile_candidate,
)


CANDIDATES = (
    ("standard", 6),
    ("standard", 7),
    ("log_standard", 2),
    ("log_standard", 3),
    ("log_standard", 4),
    ("log_standard", 5),
    ("log_robust", 2),
)


def parse_args() -> argparse.Namespace:
    project_root = Path(__file__).resolve().parents[2]
    parser = argparse.ArgumentParser(description="Generate candidate cluster profiles.")
    parser.add_argument(
        "--processed-dir",
        type=Path,
        default=project_root / "data" / "processed",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=project_root / "data" / "experiments" / "cluster_profiles",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    original = pd.read_csv(args.processed_dir / "customer_features.csv")
    comparison_rows = []

    for strategy, k in CANDIDATES:
        transformed = pd.read_csv(
            args.processed_dir / f"clustering_features_{strategy}.csv"
        )
        result = profile_candidate(
            transformed,
            original,
            preprocessing_strategy=strategy,
            k=k,
            random_state=42,
        )
        output_path = args.output_dir / f"{strategy}_k{k}_profiles.csv"
        result.profiles.to_csv(output_path, index=False)

        comparison_columns = [
            "preprocessing_strategy",
            "k",
            "cluster",
            "customer_count",
            "cluster_percentage",
            *[f"median_{feature}" for feature in BEHAVIORAL_FEATURES],
        ]
        comparison_rows.append(result.profiles.loc[:, comparison_columns])
        print(f"Created {output_path} with {len(result.profiles)} clusters.")

    comparison = pd.concat(comparison_rows, ignore_index=True)
    comparison.to_csv(
        args.output_dir.parent / "cluster_profile_comparison.csv",
        index=False,
    )
    print(f"Created comparison with {len(comparison)} cluster rows.")


if __name__ == "__main__":
    main()
