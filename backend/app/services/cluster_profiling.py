"""Profile K-Means assignments in original customer-behavior units."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from app.services.kmeans_experiments import run_kmeans


BEHAVIORAL_FEATURES = (
    "Recency",
    "Frequency",
    "MonetaryValue",
    "TotalItems",
    "UniqueProducts",
    "AverageOrderValue",
    "AverageItemsPerOrder",
    "CustomerLifetimeDays",
)


class ClusterProfilingError(ValueError):
    """Raised when assignments cannot be joined safely to original customers."""


@dataclass(frozen=True)
class ClusterProfileResult:
    assignments: pd.DataFrame
    profiles: pd.DataFrame
    overall_medians: pd.Series


def relative_indicator(cluster_median: float, overall_median: float) -> str:
    """Classify a cluster median by its ratio to the overall median."""
    if overall_median <= 0:
        raise ClusterProfilingError(
            "Relative indicators require a positive overall median."
        )
    ratio = cluster_median / overall_median
    if ratio <= 0.5:
        return "substantially below overall median"
    if ratio < 0.8:
        return "below overall median"
    if ratio <= 1.25:
        return "near overall median"
    if ratio <= 2.0:
        return "above overall median"
    return "substantially above overall median"


def profile_candidate(
    transformed: pd.DataFrame,
    original: pd.DataFrame,
    preprocessing_strategy: str,
    k: int,
    random_state: int = 42,
) -> ClusterProfileResult:
    """Fit K-Means on transformed data and profile labels on original data."""
    required_original = ["CustomerID", "Country", *BEHAVIORAL_FEATURES]
    missing = [name for name in required_original if name not in original.columns]
    if missing:
        raise ClusterProfilingError(
            f"Original customer data is missing columns: {', '.join(missing)}"
        )
    if "CustomerID" not in transformed.columns:
        raise ClusterProfilingError("Transformed data must contain CustomerID.")
    if original["CustomerID"].duplicated().any():
        raise ClusterProfilingError("Original CustomerID values must be unique.")
    if transformed["CustomerID"].duplicated().any():
        raise ClusterProfilingError("Transformed CustomerID values must be unique.")

    transformed_ids = transformed["CustomerID"].copy(deep=True)
    clustering_features = transformed.drop(columns="CustomerID").copy(deep=True)
    run = run_kmeans(clustering_features, k=k, random_state=random_state)
    assignments = pd.DataFrame(
        {"CustomerID": transformed_ids.to_numpy(copy=True), "cluster": run.labels}
    )

    profiled = assignments.merge(
        original.loc[:, required_original].copy(deep=True),
        on="CustomerID",
        how="left",
        validate="one_to_one",
        sort=False,
    )
    if len(profiled) != len(transformed):
        raise ClusterProfilingError("Customer count changed during the profile join.")
    if profiled.loc[:, required_original[1:]].isna().any().any():
        raise ClusterProfilingError(
            "At least one transformed CustomerID has no original customer record."
        )

    overall_medians = original.loc[:, BEHAVIORAL_FEATURES].median()
    grouped = profiled.groupby("cluster", sort=True)
    profiles = grouped[list(BEHAVIORAL_FEATURES)].agg(["median", "mean"])
    profiles.columns = [f"{stat}_{feature}" for feature, stat in profiles.columns]
    profiles = profiles.reset_index()
    counts = grouped.size().rename("customer_count")
    profiles.insert(1, "customer_count", profiles["cluster"].map(counts))
    profiles.insert(
        2,
        "cluster_percentage",
        profiles["customer_count"] / len(profiled) * 100,
    )
    profiles.insert(0, "k", k)
    profiles.insert(0, "preprocessing_strategy", preprocessing_strategy)

    for feature in BEHAVIORAL_FEATURES:
        profiles[f"relative_{feature}"] = profiles[f"median_{feature}"].map(
            lambda value, feature=feature: relative_indicator(
                value, overall_medians[feature]
            )
        )

    return ClusterProfileResult(
        assignments=profiled,
        profiles=profiles,
        overall_medians=overall_medians,
    )


def profile_assignments(
    customer_ids: pd.Series,
    labels: object,
    original: pd.DataFrame,
    algorithm: str,
    configuration: str,
    excluded_label: int | None = None,
) -> pd.DataFrame:
    """Profile externally generated labels using medians in original units."""
    required = ["CustomerID", *BEHAVIORAL_FEATURES]
    missing = [name for name in required if name not in original.columns]
    if missing:
        raise ClusterProfilingError(
            f"Original customer data is missing columns: {', '.join(missing)}"
        )
    label_values = list(labels)
    if len(customer_ids) != len(label_values):
        raise ClusterProfilingError("CustomerID and label row counts must match.")
    assignments = pd.DataFrame(
        {"CustomerID": customer_ids.to_numpy(copy=True), "cluster": label_values}
    )
    profiled = assignments.merge(
        original.loc[:, required].copy(deep=True),
        on="CustomerID", how="left", validate="one_to_one", sort=False,
    )
    if profiled.loc[:, BEHAVIORAL_FEATURES].isna().any().any():
        raise ClusterProfilingError("At least one CustomerID has no original record.")
    included = profiled if excluded_label is None else profiled[profiled["cluster"] != excluded_label]
    grouped = included.groupby("cluster", sort=True)
    result = grouped[list(BEHAVIORAL_FEATURES)].median().add_prefix("median_").reset_index()
    counts = grouped.size()
    result.insert(1, "customer_count", result["cluster"].map(counts))
    result.insert(2, "cluster_percentage", result["customer_count"] / len(profiled) * 100)
    result.insert(0, "configuration", configuration)
    result.insert(0, "algorithm", algorithm)
    return result
