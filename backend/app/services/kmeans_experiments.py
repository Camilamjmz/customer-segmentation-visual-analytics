"""Reusable K-Means experiment utilities for prepared customer matrices."""

from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
from pathlib import Path

import numpy as np
import pandas as pd
from pandas.api.types import is_numeric_dtype
from sklearn.cluster import KMeans
from sklearn.metrics import (
    adjusted_rand_score,
    calinski_harabasz_score,
    davies_bouldin_score,
    silhouette_score,
)


N_INIT = 20


class KMeansExperimentError(ValueError):
    """Raised when an experiment input or configuration is invalid."""


@dataclass(frozen=True)
class ClusteringDataset:
    customer_ids: pd.Series
    features: pd.DataFrame


@dataclass(frozen=True)
class KMeansRunResult:
    labels: np.ndarray
    silhouette_score: float
    davies_bouldin: float
    calinski_harabasz: float
    cluster_sizes: dict[int, int]
    smallest_cluster_size: int
    largest_cluster_size: int
    smallest_cluster_percentage: float
    largest_cluster_percentage: float


def load_clustering_dataset(path: str | Path) -> ClusteringDataset:
    """Load a prepared matrix and keep CustomerID outside the feature space."""
    data = pd.read_csv(Path(path))
    if "CustomerID" not in data.columns:
        raise KMeansExperimentError("Dataset must contain a CustomerID column.")

    feature_names = [name for name in data.columns if name != "CustomerID"]
    if not feature_names:
        raise KMeansExperimentError("Dataset contains no clustering features.")

    nonnumeric = [name for name in feature_names if not is_numeric_dtype(data[name])]
    if nonnumeric:
        raise KMeansExperimentError(
            f"Clustering features must be numeric: {', '.join(nonnumeric)}"
        )

    customer_ids = data["CustomerID"].copy(deep=True).reset_index(drop=True)
    features = data.loc[:, feature_names].copy(deep=True).reset_index(drop=True)
    values = features.to_numpy(dtype=float)

    if customer_ids.isna().any():
        raise KMeansExperimentError("CustomerID contains missing values.")
    if features.isna().any().any():
        raise KMeansExperimentError("Clustering features contain missing values.")
    if not np.isfinite(values).all():
        raise KMeansExperimentError("Clustering features contain infinite values.")

    return ClusteringDataset(customer_ids=customer_ids, features=features)


def run_kmeans(
    features: pd.DataFrame,
    k: int,
    random_state: int = 42,
) -> KMeansRunResult:
    """Fit one reproducible K-Means model and calculate diagnostics."""
    if "CustomerID" in features.columns:
        raise KMeansExperimentError("CustomerID must not be used as a feature.")
    if k < 2 or k >= len(features):
        raise KMeansExperimentError("k must be at least 2 and below the row count.")

    values = features.to_numpy(dtype=float)
    if not np.isfinite(values).all():
        raise KMeansExperimentError("Features must contain only finite values.")

    model = KMeans(n_clusters=k, random_state=random_state, n_init=N_INIT)
    labels = model.fit_predict(values)
    unique_labels, counts = np.unique(labels, return_counts=True)
    if len(unique_labels) != k:
        raise KMeansExperimentError(
            f"K-Means produced {len(unique_labels)} clusters instead of {k}."
        )

    cluster_sizes = {
        int(label): int(count) for label, count in zip(unique_labels, counts)
    }
    smallest = int(counts.min())
    largest = int(counts.max())
    row_count = len(features)

    return KMeansRunResult(
        labels=labels.copy(),
        silhouette_score=float(silhouette_score(values, labels)),
        davies_bouldin=float(davies_bouldin_score(values, labels)),
        calinski_harabasz=float(calinski_harabasz_score(values, labels)),
        cluster_sizes=cluster_sizes,
        smallest_cluster_size=smallest,
        largest_cluster_size=largest,
        smallest_cluster_percentage=smallest / row_count * 100,
        largest_cluster_percentage=largest / row_count * 100,
    )


def mean_pairwise_ari(label_sets: list[np.ndarray]) -> float:
    """Return mean ARI across every pair of random-seed solutions."""
    if len(label_sets) < 2:
        raise KMeansExperimentError("At least two label sets are required for ARI.")
    scores = [
        adjusted_rand_score(first, second)
        for first, second in combinations(label_sets, 2)
    ]
    return float(np.mean(scores))
