"""Compare preprocessing strategies using controlled K-Means runs."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

import pandas as pd


BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.services.kmeans_experiments import (  # noqa: E402
    load_clustering_dataset,
    mean_pairwise_ari,
    run_kmeans,
)


STRATEGIES = ("standard", "log_standard", "log_robust")
K_VALUES = tuple(range(2, 9))
RANDOM_STATES = (42, 7, 21, 84, 123)


def parse_args() -> argparse.Namespace:
    project_root = Path(__file__).resolve().parents[2]
    parser = argparse.ArgumentParser(
        description="Run the controlled K-Means preprocessing comparison."
    )
    parser.add_argument(
        "--processed-dir",
        type=Path,
        default=project_root / "data" / "processed",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=project_root / "data" / "experiments",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    run_rows: list[dict[str, object]] = []
    ari_by_group: dict[tuple[str, int], float] = {}

    for strategy in STRATEGIES:
        input_path = (
            args.processed_dir / f"clustering_features_{strategy}.csv"
        )
        dataset = load_clustering_dataset(input_path)

        for k in K_VALUES:
            label_sets = []
            for random_state in RANDOM_STATES:
                result = run_kmeans(dataset.features, k, random_state)
                label_sets.append(result.labels)
                run_rows.append(
                    {
                        "preprocessing_strategy": strategy,
                        "k": k,
                        "random_state": random_state,
                        "silhouette_score": result.silhouette_score,
                        "davies_bouldin": result.davies_bouldin,
                        "calinski_harabasz": result.calinski_harabasz,
                        "cluster_sizes": json.dumps(result.cluster_sizes),
                        "smallest_cluster_size": result.smallest_cluster_size,
                        "largest_cluster_size": result.largest_cluster_size,
                        "smallest_cluster_percentage": (
                            result.smallest_cluster_percentage
                        ),
                        "largest_cluster_percentage": (
                            result.largest_cluster_percentage
                        ),
                    }
                )
                print(f"Completed {strategy}, k={k}, seed={random_state}")

            ari_by_group[(strategy, k)] = mean_pairwise_ari(label_sets)

    runs = pd.DataFrame(run_rows)
    summary = (
        runs.groupby(["preprocessing_strategy", "k"], sort=False)
        .agg(
            mean_silhouette=("silhouette_score", "mean"),
            std_silhouette=("silhouette_score", "std"),
            mean_davies_bouldin=("davies_bouldin", "mean"),
            std_davies_bouldin=("davies_bouldin", "std"),
            mean_calinski_harabasz=("calinski_harabasz", "mean"),
            std_calinski_harabasz=("calinski_harabasz", "std"),
            average_smallest_cluster_percentage=(
                "smallest_cluster_percentage",
                "mean",
            ),
            average_largest_cluster_percentage=(
                "largest_cluster_percentage",
                "mean",
            ),
        )
        .reset_index()
    )
    summary["mean_pairwise_ari"] = [
        ari_by_group[(row.preprocessing_strategy, row.k)]
        for row in summary.itertuples(index=False)
    ]

    runs.to_csv(
        args.output_dir / "kmeans_preprocessing_comparison.csv",
        index=False,
    )
    summary.to_csv(
        args.output_dir / "kmeans_preprocessing_summary.csv",
        index=False,
    )
    print(f"Saved {len(runs)} run rows and {len(summary)} summary rows.")


if __name__ == "__main__":
    main()
