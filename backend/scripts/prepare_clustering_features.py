"""Generate reproducible preprocessing variants for future clustering."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys


BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.services.preprocessing import (  # noqa: E402
    PRIMARY_FEATURES,
    load_customer_features,
    preprocess_customer_features,
)


STRATEGIES = ("standard", "log_standard", "log_robust")


def parse_args() -> argparse.Namespace:
    project_root = Path(__file__).resolve().parents[2]
    parser = argparse.ArgumentParser(
        description="Create three scaled customer feature datasets."
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=project_root / "data" / "processed" / "customer_features.csv",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=project_root / "data" / "processed",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    customers = load_customer_features(args.input)
    args.output_dir.mkdir(parents=True, exist_ok=True)

    for strategy in STRATEGIES:
        result = preprocess_customer_features(
            customers,
            strategy=strategy,
            features=PRIMARY_FEATURES,
        )
        output_path = args.output_dir / f"clustering_features_{strategy}.csv"
        output = result.to_dataframe()
        output.to_csv(output_path, index=False)
        print(f"Created {output_path} with shape {output.shape}")


if __name__ == "__main__":
    main()
