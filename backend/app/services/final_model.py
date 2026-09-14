"""Freeze and serve the validated final customer segmentation."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from app.services.kmeans_experiments import load_clustering_dataset, run_kmeans

BEHAVIORAL_FEATURES = ["Recency", "Frequency", "MonetaryValue", "TotalItems", "UniqueProducts", "AverageOrderValue", "AverageItemsPerOrder", "CustomerLifetimeDays"]
CLUSTERING_FEATURES = ["Recency", "Frequency", "MonetaryValue", "UniqueProducts", "CustomerLifetimeDays"]
SEGMENT_NAMES = {0: "Inactive Low-Activity", 1: "Developing / Moderate", 2: "Recent High-Activity"}


def project_root() -> Path:
    return Path(__file__).resolve().parents[3]


def build_final_artifacts(root: Path | None = None) -> tuple[pd.DataFrame, dict]:
    """Reproduce stable final assignments and metadata from verified inputs."""
    root = root or project_root()
    prepared = load_clustering_dataset(root / "data/processed/clustering_features_log_standard.csv")
    original = pd.read_csv(root / "data/processed/customer_features.csv")
    run = run_kmeans(prepared.features, k=3, random_state=42)
    assignments = pd.DataFrame({"CustomerID": prepared.customer_ids, "raw_kmeans_label": run.labels})
    joined = assignments.merge(original, on="CustomerID", how="left", validate="one_to_one", sort=False)
    profiles = joined.groupby("raw_kmeans_label")[BEHAVIORAL_FEATURES].median()
    high_label = int(profiles["Frequency"].idxmax())
    inactive_label = int(profiles.drop(index=high_label)["Recency"].idxmax())
    developing_label = int(next(label for label in profiles.index if label not in {high_label, inactive_label}))
    raw_to_stable = {inactive_label: 0, developing_label: 1, high_label: 2}
    joined["SegmentID"] = joined.pop("raw_kmeans_label").map(raw_to_stable).astype(int)
    joined["SegmentName"] = joined["SegmentID"].map(SEGMENT_NAMES)
    columns = ["CustomerID", "SegmentID", "SegmentName", "Country", *BEHAVIORAL_FEATURES]
    final = joined.loc[:, columns].sort_values("CustomerID").reset_index(drop=True)
    counts = final.groupby(["SegmentID", "SegmentName"]).size()
    validation = pd.read_csv(root / "data/experiments/final_validation/final_validation_summary.csv")
    selected_validation = validation[validation["candidate"].str.endswith("k=3")].iloc[0]
    metadata = {
        "algorithm": "K-Means", "k": 3, "preprocessing_strategy": "log_standard",
        "clustering_features": CLUSTERING_FEATURES, "random_state": 42, "n_init": 20,
        "customer_count": len(final), "silhouette_score": run.silhouette_score,
        "davies_bouldin_score": run.davies_bouldin,
        "calinski_harabasz_score": run.calinski_harabasz,
        "cluster_counts": {str(i): int(counts.loc[(i, SEGMENT_NAMES[i])]) for i in SEGMENT_NAMES},
        "cluster_percentages": {str(i): float(counts.loc[(i, SEGMENT_NAMES[i])] / len(final) * 100) for i in SEGMENT_NAMES},
        "raw_label_to_stable_segment": {str(raw): stable for raw, stable in raw_to_stable.items()},
        "segment_names": {str(key): value for key, value in SEGMENT_NAMES.items()},
        "mapping_method": "Highest median Frequency is Recent High-Activity; among remaining clusters, highest median Recency is Inactive Low-Activity; the remaining cluster is Developing / Moderate.",
        "validation_summary": {
            "random_initialization_stability_ari": float(selected_validation["random_initialization_stability_ari"]),
            "subsampling_mean_ari": float(selected_validation["subsampling_mean_ari"]),
            "feature_sensitivity_ari": float(selected_validation["feature_sensitivity_ari"]),
            "full_customer_coverage": bool(selected_validation["full_customer_coverage"]),
        },
        "selected_model_rationale": "Best full-coverage internal metrics, balanced interpretable groups, strong subsampling stability, and greater parsimony than k=4.",
        "sensitivity_model_information": {"algorithm": "K-Means", "preprocessing_strategy": "log_standard", "k": 4, "role": "Sensitivity model only; it adds a recent low-frequency segment."},
    }
    if final.isna().any().any() or not np.isfinite(final[BEHAVIORAL_FEATURES].to_numpy(float)).all():
        raise RuntimeError("Final segmentation contains invalid values.")
    return final, metadata


def save_final_artifacts(root: Path | None = None) -> tuple[Path, Path]:
    root = root or project_root()
    final, metadata = build_final_artifacts(root)
    output = root / "data/final"; output.mkdir(parents=True, exist_ok=True)
    csv_path = output / "final_customer_segments.csv"
    json_path = output / "final_model_summary.json"
    final.to_csv(csv_path, index=False)
    json_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    return csv_path, json_path


def comparison_text(feature: str, value: float, population: float) -> str:
    ratio = value / population if population else 1.0
    direction = "lower" if ratio < 1 else "higher"
    degree = "substantially " if ratio < 0.5 or ratio > 2 else ""
    if feature == "Recency":
        return f"Median Recency is {degree}{direction} than the population median; lower Recency means more recent purchasing activity."
    return f"Median {feature} is {degree}{direction} than the population median."


def segment_analytics(customers: pd.DataFrame) -> tuple[list[dict], dict[int, dict]]:
    population_medians = customers[BEHAVIORAL_FEATURES].median()
    summaries, details = [], {}
    for (segment_id, name), group in customers.groupby(["SegmentID", "SegmentName"], sort=True):
        medians = group[BEHAVIORAL_FEATURES].median().to_dict()
        means = group[BEHAVIORAL_FEATURES].mean().to_dict()
        comparisons = {feature: comparison_text(feature, medians[feature], population_medians[feature]) for feature in BEHAVIORAL_FEATURES}
        insights = [comparisons["Recency"], comparisons["Frequency"], comparisons["MonetaryValue"]]
        summary = {"SegmentID": int(segment_id), "SegmentName": name, "customer_count": len(group), "customer_percentage": len(group) / len(customers) * 100, "median_profile": medians, "key_insights": insights}
        summaries.append(summary)
        details[int(segment_id)] = {**summary, "mean_profile": means, "population_medians": population_medians.to_dict(), "comparison_with_population": comparisons, "key_characteristics": insights, "interpretation_notes": [f"This descriptive profile summarizes observed behavior for {len(group):,} customers."], "limitations": ["Segment membership describes historical purchasing behavior and does not establish customer intent or causality.", "Positive outliers were retained, so means can be influenced by unusually large customers."]}
    return summaries, details
