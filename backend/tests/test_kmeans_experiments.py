"""Focused tests for the controlled K-Means service."""

import unittest

import numpy as np
import pandas as pd

from app.services.kmeans_experiments import (
    KMeansExperimentError,
    run_kmeans,
)


class KMeansExperimentTests(unittest.TestCase):
    def setUp(self) -> None:
        rng = np.random.default_rng(42)
        first = rng.normal(loc=-3, scale=0.2, size=(20, 2))
        second = rng.normal(loc=3, scale=0.2, size=(20, 2))
        self.features = pd.DataFrame(
            np.vstack([first, second]), columns=["FeatureA", "FeatureB"]
        )

    def test_customer_id_is_rejected_as_a_feature(self) -> None:
        invalid = self.features.assign(CustomerID=range(len(self.features)))
        with self.assertRaisesRegex(KMeansExperimentError, "CustomerID"):
            run_kmeans(invalid, k=2)

    def test_expected_label_count_and_cluster_count(self) -> None:
        result = run_kmeans(self.features, k=2)
        self.assertEqual(len(result.labels), len(self.features))
        self.assertEqual(len(np.unique(result.labels)), 2)

    def test_same_random_state_is_reproducible(self) -> None:
        first = run_kmeans(self.features, k=2, random_state=42)
        second = run_kmeans(self.features, k=2, random_state=42)
        np.testing.assert_array_equal(first.labels, second.labels)

    def test_metrics_are_finite(self) -> None:
        result = run_kmeans(self.features, k=2)
        metrics = [
            result.silhouette_score,
            result.davies_bouldin,
            result.calinski_harabasz,
        ]
        self.assertTrue(np.isfinite(metrics).all())

    def test_cluster_sizes_sum_to_row_count(self) -> None:
        result = run_kmeans(self.features, k=2)
        self.assertEqual(sum(result.cluster_sizes.values()), len(self.features))


if __name__ == "__main__":
    unittest.main()
