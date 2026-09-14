"""Run final subsampling and feature-sensitivity validation."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import adjusted_rand_score

BACKEND = Path(__file__).resolve().parents[1]
ROOT = BACKEND.parent
sys.path.insert(0, str(BACKEND))

from app.services.cluster_profiling import profile_assignments
from app.services.final_validation import evaluate_subsample
from app.services.kmeans_experiments import N_INIT, load_clustering_dataset, run_kmeans
from app.services.preprocessing import preprocess_customer_features

ALTERNATIVE_FEATURES = (
    "Recency", "Frequency", "TotalItems", "UniqueProducts", "CustomerLifetimeDays"
)
ALTERNATIVE_LOG_FEATURES = ("Frequency", "TotalItems", "UniqueProducts")
SEEDS = tuple(range(1000, 1020))


def main() -> None:
    output_dir = ROOT / "data/experiments/final_validation"
    output_dir.mkdir(parents=True, exist_ok=True)
    primary = load_clustering_dataset(
        ROOT / "data/processed/clustering_features_log_standard.csv"
    )
    original = pd.read_csv(ROOT / "data/processed/customer_features.csv")
    alternative = preprocess_customer_features(
        original, strategy="log_standard", features=ALTERNATIVE_FEATURES,
        log_features=ALTERNATIVE_LOG_FEATURES,
    )
    if not primary.customer_ids.equals(alternative.customer_ids):
        raise RuntimeError("Primary and alternative CustomerID order differs.")

    subsampling_rows = []
    reference_models = {}
    for k in (3, 4):
        reference = KMeans(n_clusters=k, random_state=42, n_init=N_INIT).fit(primary.features)
        reference_models[k] = reference
        for seed in SEEDS:
            result = evaluate_subsample(
                primary.features, reference.labels_, reference.cluster_centers_, k, seed
            )
            subsampling_rows.append({
                "k": k, "iteration_seed": seed, "sample_proportion": 0.8,
                "sample_size": result.sample_size,
                "adjusted_rand_index": result.adjusted_rand_index,
                "mean_absolute_cluster_percentage_difference": result.mean_absolute_cluster_percentage_difference,
                "cluster_size_stability": result.cluster_size_stability,
                "mean_centroid_distance": result.mean_centroid_distance,
                "max_centroid_distance": result.max_centroid_distance,
                "cluster_sizes": json.dumps(result.cluster_sizes, sort_keys=True),
            })
    subsampling = pd.DataFrame(subsampling_rows)
    subsampling.to_csv(output_dir / "subsampling_stability.csv", index=False)

    sensitivity_rows = []
    for k in (3, 4):
        primary_run = run_kmeans(primary.features, k=k, random_state=42)
        alternative_run = run_kmeans(alternative.matrix, k=k, random_state=42)
        ari = float(adjusted_rand_score(primary_run.labels, alternative_run.labels))
        for name, matrix, run in (
            ("MonetaryValue primary", primary.features, primary_run),
            ("TotalItems alternative", alternative.matrix, alternative_run),
        ):
            profile = profile_assignments(
                primary.customer_ids, run.labels, original, name, f"k={k}"
            )
            sensitivity_rows.append({
                "feature_specification": name, "k": k,
                "features": ", ".join(matrix.columns),
                "silhouette_score": run.silhouette_score,
                "davies_bouldin": run.davies_bouldin,
                "calinski_harabasz": run.calinski_harabasz,
                "cluster_sizes": json.dumps(run.cluster_sizes, sort_keys=True),
                "smallest_cluster_percentage": run.smallest_cluster_percentage,
                "largest_cluster_percentage": run.largest_cluster_percentage,
                "ari_vs_primary": 1.0 if name.startswith("MonetaryValue") else ari,
                "original_unit_cluster_profiles": profile.to_json(orient="records"),
            })
    sensitivity = pd.DataFrame(sensitivity_rows)
    sensitivity.to_csv(output_dir / "feature_sensitivity.csv", index=False)

    stability = subsampling.groupby("k").agg(
        mean_ari=("adjusted_rand_index", "mean"),
        std_ari=("adjusted_rand_index", "std"),
        minimum_ari=("adjusted_rand_index", "min"),
        maximum_ari=("adjusted_rand_index", "max"),
        mean_cluster_size_stability=("cluster_size_stability", "mean"),
        mean_cluster_percentage_variation=("mean_absolute_cluster_percentage_difference", "mean"),
        mean_centroid_distance=("mean_centroid_distance", "mean"),
        maximum_centroid_distance=("max_centroid_distance", "max"),
    ).reset_index()
    decisions = []
    previous = pd.read_csv(ROOT / "data/experiments/algorithm_comparison/algorithm_comparison.csv")
    prior_random = pd.read_csv(ROOT / "data/experiments/kmeans_preprocessing_summary.csv")
    for k in (3, 4):
        metric = previous[(previous.algorithm == "K-Means") & (previous.configuration == f"k={k}")].iloc[0]
        random_ari = prior_random[(prior_random.preprocessing_strategy == "log_standard") & (prior_random.k == k)].iloc[0].mean_pairwise_ari
        robust = stability[stability.k == k].iloc[0]
        alt_ari = sensitivity[(sensitivity.feature_specification == "TotalItems alternative") & (sensitivity.k == k)].iloc[0].ari_vs_primary
        decisions.append({
            "candidate": f"K-Means log_standard k={k}",
            "internal_quality": f"silhouette={metric.silhouette_score:.4f}; DB={metric.davies_bouldin:.4f}; CH={metric.calinski_harabasz:.2f}",
            "cluster_balance": f"smallest={metric.smallest_cluster_percentage:.2f}%; largest={metric.largest_cluster_percentage:.2f}%",
            "interpretability": "three broad activity levels" if k == 3 else "adds recent low-frequency separation",
            "random_initialization_stability_ari": random_ari,
            "subsampling_mean_ari": robust.mean_ari,
            "feature_sensitivity_ari": alt_ari,
            "full_customer_coverage": True,
            "simplicity_parsimony": "stronger" if k == 3 else "weaker: one additional segment",
            "decision_position": "recommended" if k == 3 else "sensitivity candidate",
        })
    pd.DataFrame(decisions).to_csv(output_dir / "final_validation_summary.csv", index=False)
    print(stability.to_string(index=False))
    print(sensitivity.to_string(index=False))


if __name__ == "__main__":
    main()
