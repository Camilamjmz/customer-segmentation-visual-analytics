"""DBSCAN utilities with explicit treatment of noise observations."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from sklearn.cluster import DBSCAN
from sklearn.metrics import calinski_harabasz_score, davies_bouldin_score, silhouette_score


class DBSCANClusteringError(ValueError):
    """Raised when DBSCAN input or configuration is invalid."""


@dataclass(frozen=True)
class DBSCANResult:
    labels: np.ndarray
    n_clusters: int
    noise_count: int
    noise_percentage: float
    silhouette_score: float | None
    davies_bouldin: float | None
    calinski_harabasz: float | None
    cluster_sizes: dict[int, int]
    smallest_cluster_percentage: float | None
    largest_cluster_percentage: float | None
    fewer_than_two_clusters: bool
    noise_over_30_percent: bool
    has_cluster_below_1_percent: bool


def run_dbscan(features: pd.DataFrame, eps: float, min_samples: int) -> DBSCANResult:
    """Run DBSCAN and score only non-noise customers when scoring is valid."""
    if "CustomerID" in features.columns:
        raise DBSCANClusteringError("CustomerID must not be used as a feature.")
    if eps <= 0 or min_samples < 1:
        raise DBSCANClusteringError("eps must be positive and min_samples at least 1.")
    values = features.to_numpy(dtype=float)
    if not np.isfinite(values).all():
        raise DBSCANClusteringError("Features must contain only finite values.")

    labels = DBSCAN(eps=eps, min_samples=min_samples).fit_predict(values)
    non_noise = labels != -1
    cluster_labels, counts = np.unique(labels[non_noise], return_counts=True)
    sizes = {int(label): int(count) for label, count in zip(cluster_labels, counts)}
    n_clusters = len(cluster_labels)
    noise_count = int((~non_noise).sum())
    total = len(labels)
    valid_metrics = n_clusters >= 2 and int(non_noise.sum()) > n_clusters
    if valid_metrics:
        scored_values = values[non_noise]
        scored_labels = labels[non_noise]
        silhouette = float(silhouette_score(scored_values, scored_labels))
        davies_bouldin = float(davies_bouldin_score(scored_values, scored_labels))
        calinski_harabasz = float(
            calinski_harabasz_score(scored_values, scored_labels)
        )
    else:
        silhouette = davies_bouldin = calinski_harabasz = None

    minimum = float(counts.min() / total * 100) if len(counts) else None
    maximum = float(counts.max() / total * 100) if len(counts) else None
    return DBSCANResult(
        labels=labels.copy(),
        n_clusters=n_clusters,
        noise_count=noise_count,
        noise_percentage=noise_count / total * 100,
        silhouette_score=silhouette,
        davies_bouldin=davies_bouldin,
        calinski_harabasz=calinski_harabasz,
        cluster_sizes=sizes,
        smallest_cluster_percentage=minimum,
        largest_cluster_percentage=maximum,
        fewer_than_two_clusters=n_clusters < 2,
        noise_over_30_percent=noise_count / total > 0.30,
        has_cluster_below_1_percent=minimum is not None and minimum < 1.0,
    )
