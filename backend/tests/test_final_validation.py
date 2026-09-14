import unittest
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans

from app.services.final_validation import draw_subsample_indices, evaluate_subsample
from app.services.preprocessing import preprocess_customer_features


class FinalValidationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        root = Path(__file__).resolve().parents[2]
        cls.original = pd.read_csv(root / "data/processed/customer_features.csv")
        prepared = pd.read_csv(root / "data/processed/clustering_features_log_standard.csv")
        cls.primary = prepared.drop(columns="CustomerID")

    def test_subsample_uses_requested_proportion_without_replacement(self):
        indices = draw_subsample_indices(5878, 0.8, 1000)
        self.assertEqual(len(indices), round(5878 * 0.8))
        self.assertEqual(len(np.unique(indices)), len(indices))

    def test_customer_id_is_not_a_clustering_feature(self):
        model = KMeans(n_clusters=3, random_state=42, n_init=20).fit(self.primary)
        invalid = self.primary.assign(CustomerID=np.arange(len(self.primary)))
        with self.assertRaisesRegex(ValueError, "CustomerID"):
            evaluate_subsample(invalid, model.labels_, model.cluster_centers_, 3, 1000)

    def test_subsample_metrics_and_sizes_are_valid(self):
        model = KMeans(n_clusters=3, random_state=42, n_init=20).fit(self.primary)
        result = evaluate_subsample(
            self.primary, model.labels_, model.cluster_centers_, 3, 1000
        )
        self.assertGreaterEqual(result.adjusted_rand_index, -1)
        self.assertLessEqual(result.adjusted_rand_index, 1)
        self.assertEqual(sum(result.cluster_sizes.values()), result.sample_size)

    def test_alternative_preprocessing_is_finite_and_uses_total_items(self):
        features = (
            "Recency", "Frequency", "TotalItems", "UniqueProducts",
            "CustomerLifetimeDays",
        )
        result = preprocess_customer_features(
            self.original, "log_standard", features,
            log_features=("Frequency", "TotalItems", "UniqueProducts"),
        )
        self.assertIn("TotalItems", result.matrix.columns)
        self.assertNotIn("MonetaryValue", result.matrix.columns)
        self.assertFalse(result.matrix.isna().any().any())
        self.assertTrue(np.isfinite(result.matrix.to_numpy()).all())


if __name__ == "__main__":
    unittest.main()
