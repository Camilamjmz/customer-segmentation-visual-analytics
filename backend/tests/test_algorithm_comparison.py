import numpy as np
import pandas as pd
import unittest
from pathlib import Path

from app.services.dbscan_clustering import run_dbscan
from app.services.hierarchical_clustering import run_hierarchical


def three_groups() -> pd.DataFrame:
    rng = np.random.default_rng(42)
    return pd.DataFrame(np.vstack([
        rng.normal(-4, 0.15, (20, 5)), rng.normal(0, 0.15, (20, 5)),
        rng.normal(4, 0.15, (20, 5)),
    ]), columns=list("abcde"))


class AlgorithmComparisonTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        path = Path(__file__).resolve().parents[2] / "data/processed/clustering_features_log_standard.csv"
        cls.real_data = pd.read_csv(path).drop(columns="CustomerID")

    def test_hierarchical_preserves_rows_and_reports_sizes(self):
        data = three_groups()
        result = run_hierarchical(data, n_clusters=3)
        self.assertEqual(len(result.labels), len(data))
        self.assertEqual(sum(result.cluster_sizes.values()), len(data))
        self.assertEqual(len(result.cluster_sizes), 3)
        self.assertTrue(np.isfinite([
            result.silhouette_score, result.davies_bouldin,
            result.calinski_harabasz,
        ]).all())

    def test_dbscan_noise_and_clusters_sum_to_total(self):
        data = three_groups()
        result = run_dbscan(data, eps=0.8, min_samples=4)
        self.assertEqual(len(result.labels), len(data))
        self.assertEqual(sum(result.cluster_sizes.values()) + result.noise_count, len(data))
        self.assertGreaterEqual(result.n_clusters, 2)
        self.assertIsNotNone(result.silhouette_score)

    def test_dbscan_omits_metrics_with_fewer_than_two_clusters(self):
        data = pd.DataFrame(np.zeros((10, 2)), columns=["x", "y"])
        result = run_dbscan(data, eps=1.0, min_samples=2)
        self.assertTrue(result.fewer_than_two_clusters)
        self.assertIsNone(result.silhouette_score)
        self.assertIsNone(result.davies_bouldin)
        self.assertIsNone(result.calinski_harabasz)

    def test_hierarchical_real_dataset_covers_5878_customers(self):
        result = run_hierarchical(self.real_data, n_clusters=3)
        self.assertEqual(len(result.labels), 5878)
        self.assertEqual(len(result.cluster_sizes), 3)
        self.assertEqual(sum(result.cluster_sizes.values()), 5878)
        self.assertTrue(np.isfinite([
            result.silhouette_score, result.davies_bouldin,
            result.calinski_harabasz,
        ]).all())

    def test_dbscan_real_dataset_accounts_for_5878_customers(self):
        result = run_dbscan(self.real_data, eps=0.5, min_samples=20)
        self.assertEqual(len(result.labels), 5878)
        self.assertEqual(sum(result.cluster_sizes.values()) + result.noise_count, 5878)
        self.assertNotIn(-1, result.cluster_sizes)


if __name__ == "__main__":
    unittest.main()
