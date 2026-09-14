"""Reusable robustness utilities for final K-Means validation."""

from __future__ import annotations

from dataclasses import dataclass
from itertools import permutations

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import adjusted_rand_score

from app.services.kmeans_experiments import N_INIT


class FinalValidationError(ValueError):
    """Raised when a robustness experiment configuration is invalid."""


@dataclass(frozen=True)
class SubsampleResult:
    seed: int
    sample_size: int
    adjusted_rand_index: float
    mean_absolute_cluster_percentage_difference: float
    cluster_size_stability: float
    mean_centroid_distance: float
    max_centroid_distance: float
    cluster_sizes: dict[int, int]


def draw_subsample_indices(row_count: int, proportion: float, seed: int) -> np.ndarray:
    """Return a reproducible sample without replacement."""
    if row_count < 2 or not 0 < proportion <= 1:
        raise FinalValidationError("row_count must exceed 1 and proportion be in (0, 1].")
    sample_size = int(round(row_count * proportion))
    return np.sort(np.random.default_rng(seed).choice(row_count, sample_size, replace=False))


def optimal_centroid_alignment(reference: np.ndarray, candidate: np.ndarray) -> tuple[int, ...]:
    """Map each reference cluster to a candidate cluster by minimum total distance."""
    if reference.shape != candidate.shape:
        raise FinalValidationError("Reference and candidate centroids must have equal shape.")
    k = len(reference)
    return min(
        permutations(range(k)),
        key=lambda order: sum(
            np.linalg.norm(reference[index] - candidate[order[index]])
            for index in range(k)
        ),
    )


def evaluate_subsample(
    features: pd.DataFrame,
    reference_labels: np.ndarray,
    reference_centroids: np.ndarray,
    k: int,
    seed: int,
    proportion: float = 0.8,
) -> SubsampleResult:
    """Fit one subsample and compare it with the full-data reference solution."""
    if "CustomerID" in features.columns:
        raise FinalValidationError("CustomerID must not be used as a feature.")
    indices = draw_subsample_indices(len(features), proportion, seed)
    sample = features.iloc[indices]
    model = KMeans(n_clusters=k, random_state=seed, n_init=N_INIT).fit(sample)
    order = optimal_centroid_alignment(reference_centroids, model.cluster_centers_)
    candidate_to_reference = {candidate: reference for reference, candidate in enumerate(order)}
    aligned_labels = np.array([candidate_to_reference[label] for label in model.labels_])
    ari = float(adjusted_rand_score(reference_labels[indices], aligned_labels))

    reference_percentages = np.bincount(reference_labels, minlength=k) / len(features) * 100
    sample_counts = np.bincount(aligned_labels, minlength=k)
    sample_percentages = sample_counts / len(sample) * 100
    size_difference = float(np.mean(np.abs(sample_percentages - reference_percentages)))
    aligned_centroids = model.cluster_centers_[list(order)]
    centroid_distances = np.linalg.norm(reference_centroids - aligned_centroids, axis=1)
    return SubsampleResult(
        seed=seed,
        sample_size=len(sample),
        adjusted_rand_index=ari,
        mean_absolute_cluster_percentage_difference=size_difference,
        cluster_size_stability=max(0.0, 1.0 - size_difference / 100),
        mean_centroid_distance=float(centroid_distances.mean()),
        max_centroid_distance=float(centroid_distances.max()),
        cluster_sizes={index: int(value) for index, value in enumerate(sample_counts)},
    )
