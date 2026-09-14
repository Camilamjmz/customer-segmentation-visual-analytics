"""Focused validation tests for the prepared customer feature table."""

from pathlib import Path
import unittest

import pandas as pd


DATA_PATH = (
    Path(__file__).resolve().parents[2]
    / "data"
    / "processed"
    / "customer_features.csv"
)


class CustomerFeaturesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.customers = pd.read_csv(DATA_PATH)

    def test_one_row_per_customer(self) -> None:
        self.assertTrue(self.customers["CustomerID"].is_unique)

    def test_customer_id_is_never_missing(self) -> None:
        self.assertFalse(self.customers["CustomerID"].isna().any())

    def test_frequency_is_positive(self) -> None:
        self.assertTrue((self.customers["Frequency"] > 0).all())

    def test_monetary_value_is_positive(self) -> None:
        self.assertTrue((self.customers["MonetaryValue"] > 0).all())

    def test_total_items_is_positive(self) -> None:
        self.assertTrue((self.customers["TotalItems"] > 0).all())

    def test_average_order_value_formula(self) -> None:
        expected = self.customers["MonetaryValue"] / self.customers["Frequency"]
        difference = (self.customers["AverageOrderValue"] - expected).abs()
        self.assertTrue((difference <= 0.01).all())

    def test_average_items_per_order_formula(self) -> None:
        expected = self.customers["TotalItems"] / self.customers["Frequency"]
        difference = (self.customers["AverageItemsPerOrder"] - expected).abs()
        self.assertTrue((difference <= 0.01).all())

    def test_recency_is_nonnegative(self) -> None:
        self.assertTrue((self.customers["Recency"] >= 0).all())


if __name__ == "__main__":
    unittest.main()
