"""Compare K-Means, Ward hierarchical clustering, and DBSCAN."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd
from sklearn.metrics import adjusted_rand_score

BACKEND = Path(__file__).resolve().parents[1]
ROOT = BACKEND.parent
sys.path.insert(0, str(BACKEND))

from app.services.cluster_profiling import profile_assignments
from app.services.dbscan_clustering import run_dbscan
from app.services.hierarchical_clustering import run_hierarchical
from app.services.kmeans_experiments import load_clustering_dataset, run_kmeans


def size_json(sizes: dict[int, int]) -> str:
    return json.dumps(sizes, sort_keys=True)


def main() -> None:
    prepared_path = ROOT / "data/processed/clustering_features_log_standard.csv"
    original_path = ROOT / "data/processed/customer_features.csv"
    output_dir = ROOT / "data/experiments/algorithm_comparison"
    output_dir.mkdir(parents=True, exist_ok=True)

    dataset = load_clustering_dataset(prepared_path)
    original = pd.read_csv(original_path)
    comparison: list[dict[str, object]] = []
    labels_by_name: dict[str, object] = {}

    kmeans_rows = []
    for k in (3, 4):
        run = run_kmeans(dataset.features, k=k, random_state=42)
        name = f"k={k}"
        labels_by_name[f"K-Means {name}"] = run.labels
        row = {
            "algorithm": "K-Means", "configuration": name, "n_clusters": k,
            "silhouette_score": run.silhouette_score,
            "davies_bouldin": run.davies_bouldin,
            "calinski_harabasz": run.calinski_harabasz,
            "smallest_cluster_percentage": run.smallest_cluster_percentage,
            "largest_cluster_percentage": run.largest_cluster_percentage,
            "noise_count": 0, "noise_percentage": 0.0,
            "cluster_sizes": size_json(run.cluster_sizes),
            "fewer_than_two_clusters": False, "noise_over_30_percent": False,
            "has_cluster_below_1_percent": run.smallest_cluster_percentage < 1,
            "metrics_population": "all customers",
        }
        comparison.append(row); kmeans_rows.append(row)

    hierarchical_rows = []
    for k in (3, 4):
        run = run_hierarchical(dataset.features, n_clusters=k)
        name = f"k={k}, linkage=ward, metric=euclidean"
        labels_by_name[f"Hierarchical {name}"] = run.labels
        row = {
            "algorithm": "Hierarchical", "configuration": name, "n_clusters": k,
            "silhouette_score": run.silhouette_score,
            "davies_bouldin": run.davies_bouldin,
            "calinski_harabasz": run.calinski_harabasz,
            "smallest_cluster_percentage": run.smallest_cluster_percentage,
            "largest_cluster_percentage": run.largest_cluster_percentage,
            "noise_count": 0, "noise_percentage": 0.0,
            "cluster_sizes": size_json(run.cluster_sizes),
            "ari_vs_corresponding_kmeans": adjusted_rand_score(
                labels_by_name[f"K-Means k={k}"], run.labels
            ),
            "fewer_than_two_clusters": False, "noise_over_30_percent": False,
            "has_cluster_below_1_percent": run.smallest_cluster_percentage < 1,
            "metrics_population": "all customers",
        }
        comparison.append(row); hierarchical_rows.append(row)

    dbscan_rows = []
    dbscan_labels: dict[str, object] = {}
    for eps in [round(value / 10, 1) for value in range(3, 11)]:
        for min_samples in (5, 10, 15, 20):
            run = run_dbscan(dataset.features, eps=eps, min_samples=min_samples)
            name = f"eps={eps:.1f}, min_samples={min_samples}"
            dbscan_labels[name] = run.labels
            row = {
                "algorithm": "DBSCAN", "configuration": name,
                "eps": eps, "min_samples": min_samples,
                "n_clusters": run.n_clusters,
                "silhouette_score": run.silhouette_score,
                "davies_bouldin": run.davies_bouldin,
                "calinski_harabasz": run.calinski_harabasz,
                "smallest_cluster_percentage": run.smallest_cluster_percentage,
                "largest_cluster_percentage": run.largest_cluster_percentage,
                "noise_count": run.noise_count,
                "noise_percentage": run.noise_percentage,
                "cluster_sizes": size_json(run.cluster_sizes),
                "fewer_than_two_clusters": run.fewer_than_two_clusters,
                "noise_over_30_percent": run.noise_over_30_percent,
                "has_cluster_below_1_percent": run.has_cluster_below_1_percent,
                "metrics_population": "non-noise customers only",
            }
            comparison.append(row); dbscan_rows.append(row)

    pd.DataFrame(hierarchical_rows).to_csv(output_dir / "hierarchical_results.csv", index=False)
    pd.DataFrame(dbscan_rows).to_csv(output_dir / "dbscan_results.csv", index=False)
    comparison_frame = pd.DataFrame(comparison)
    comparison_frame.to_csv(output_dir / "algorithm_comparison.csv", index=False)

    best_h = max(hierarchical_rows, key=lambda row: row["silhouette_score"])
    eligible_dbscan = [
        row for row in dbscan_rows
        if not row["fewer_than_two_clusters"]
        and not row["noise_over_30_percent"]
        and not row["has_cluster_below_1_percent"]
        and row["silhouette_score"] is not None
    ]
    if not eligible_dbscan:
        eligible_dbscan = [row for row in dbscan_rows if row["silhouette_score"] is not None]
    best_d = sorted(
        eligible_dbscan,
        key=lambda row: (-row["silhouette_score"], row["davies_bouldin"], -row["calinski_harabasz"]),
    )[0]

    profiles = []
    for k in (3, 4):
        profiles.append(profile_assignments(
            dataset.customer_ids, labels_by_name[f"K-Means k={k}"], original,
            "K-Means", f"k={k}",
        ))
    h_name = str(best_h["configuration"])
    profiles.append(profile_assignments(
        dataset.customer_ids, labels_by_name[f"Hierarchical {h_name}"], original,
        "Hierarchical", h_name,
    ))
    d_name = str(best_d["configuration"])
    profiles.append(profile_assignments(
        dataset.customer_ids, dbscan_labels[d_name], original,
        "DBSCAN", d_name, excluded_label=-1,
    ))
    pd.concat(profiles, ignore_index=True).to_csv(
        output_dir / "selected_algorithm_profiles.csv", index=False
    )
    print(f"Compared {len(comparison_frame)} configurations for {len(dataset.features)} customers.")
    print(f"Selected hierarchical profile: {h_name}")
    print(f"Selected DBSCAN profile: {d_name}")


if __name__ == "__main__":
    main()
