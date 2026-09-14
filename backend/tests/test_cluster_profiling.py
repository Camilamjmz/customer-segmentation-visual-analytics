"""Focused tests for original-unit cluster profiling."""

from pathlib import Path
import unittest

import pandas as pd

from app.services.cluster_profiling import (
    BEHAVIORAL_FEATURES,
    profile_candidate,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]


class ClusterProfilingTests(unittest.TestCase):
    def setUp(self) -> None:
        self.original = pd.DataFrame(
            {
                "CustomerID": [101, 102, 103, 104],
                "Country": ["A", "A", "B", "B"],
                "Recency": [5, 7, 100, 120],
                "Frequency": [10, 12, 1, 2],
                "MonetaryValue": [1000.0, 1200.0, 50.0, 60.0],
                "TotalItems": [100, 120, 5, 6],
                "UniqueProducts": [20, 22, 2, 3],
                "AverageOrderValue": [100.0, 100.0, 50.0, 30.0],
                "AverageItemsPerOrder": [10.0, 10.0, 5.0, 3.0],
                "CustomerLifetimeDays": [300, 320, 0, 5],
            }
        )
        self.transformed = pd.DataFrame(
            {
                "CustomerID": [101, 102, 103, 104],
                "Recency": [-1.0, -0.9, 0.9, 1.0],
                "Frequency": [1.0, 0.9, -0.9, -1.0],
                "MonetaryValue": [1.0, 0.9, -0.9, -1.0],
                "UniqueProducts": [1.0, 0.9, -0.9, -1.0],
                "CustomerLifetimeDays": [1.0, 0.9, -0.9, -1.0],
            }
        )

    def test_customer_ids_and_all_customers_are_preserved(self) -> None:
        result = profile_candidate(self.transformed, self.original, "test", 2)
        self.assertListEqual(
            result.assignments["CustomerID"].tolist(), [101, 102, 103, 104]
        )
        self.assertEqual(len(result.assignments), len(self.original))
        self.assertEqual(result.assignments["cluster"].notna().sum(), 4)

    def test_counts_sum_to_customer_count(self) -> None:
        result = profile_candidate(self.transformed, self.original, "test", 2)
        self.assertEqual(result.profiles["customer_count"].sum(), 4)

    def test_profiles_use_original_values_and_correct_medians(self) -> None:
        result = profile_candidate(self.transformed, self.original, "test", 2)
        expected = result.assignments.groupby("cluster")[
            list(BEHAVIORAL_FEATURES)
        ].median()
        actual = result.profiles.set_index("cluster")
        for feature in BEHAVIORAL_FEATURES:
            pd.testing.assert_series_equal(
                actual[f"median_{feature}"],
                expected[feature],
                check_names=False,
                check_index_type=False,
            )
        self.assertGreater(actual["median_MonetaryValue"].max(), 100)

    def test_generated_candidate_counts_each_sum_to_5878(self) -> None:
        path = (
            PROJECT_ROOT
            / "data"
            / "experiments"
            / "cluster_profile_comparison.csv"
        )
        if not path.exists():
            self.skipTest("Generated profile comparison is not available yet.")
        profiles = pd.read_csv(path)
        totals = profiles.groupby(["preprocessing_strategy", "k"])[
            "customer_count"
        ].sum()
        self.assertTrue((totals == 5878).all())


if __name__ == "__main__":
    unittest.main()
