"""Ward hierarchical clustering utilities for prepared customer matrices."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from sklearn.cluster import AgglomerativeClustering
from sklearn.metrics import calinski_harabasz_score, davies_bouldin_score, silhouette_score


class HierarchicalClusteringError(ValueError):
    """Raised when hierarchical clustering input is invalid."""


@dataclass(frozen=True)
class HierarchicalResult:
    labels: np.ndarray
    silhouette_score: float
    davies_bouldin: float
    calinski_harabasz: float
    cluster_sizes: dict[int, int]
    smallest_cluster_percentage: float
    largest_cluster_percentage: float


def run_hierarchical(features: pd.DataFrame, n_clusters: int) -> HierarchicalResult:
    """Run Ward linkage with Euclidean distance and calculate diagnostics."""
    if "CustomerID" in features.columns:
        raise HierarchicalClusteringError("CustomerID must not be used as a feature.")
    if n_clusters < 2 or n_clusters >= len(features):
        raise HierarchicalClusteringError(
            "n_clusters must be at least 2 and below the row count."
        )
    values = features.to_numpy(dtype=float)
    if not np.isfinite(values).all():
        raise HierarchicalClusteringError("Features must contain only finite values.")

    labels = AgglomerativeClustering(
        n_clusters=n_clusters, linkage="ward", metric="euclidean"
    ).fit_predict(values)
    unique, counts = np.unique(labels, return_counts=True)
    sizes = {int(label): int(count) for label, count in zip(unique, counts)}
    return HierarchicalResult(
        labels=labels.copy(),
        silhouette_score=float(silhouette_score(values, labels)),
        davies_bouldin=float(davies_bouldin_score(values, labels)),
        calinski_harabasz=float(calinski_harabasz_score(values, labels)),
        cluster_sizes=sizes,
        smallest_cluster_percentage=float(counts.min() / len(features) * 100),
        largest_cluster_percentage=float(counts.max() / len(features) * 100),
    )
