"""Tests for reusable clustering preprocessing."""

import unittest

import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler

from app.services.preprocessing import (
    PRIMARY_FEATURES,
    PreprocessingValidationError,
    preprocess_customer_features,
)


class PreprocessingTests(unittest.TestCase):
    def setUp(self) -> None:
        self.customers = pd.DataFrame(
            {
                "CustomerID": [30, 10, 20],
                "Country": ["A", "B", "C"],
                "Recency": [1, 10, 100],
                "Frequency": [1, 4, 20],
                "MonetaryValue": [10.0, 100.0, 1000.0],
                "UniqueProducts": [1, 5, 25],
                "CustomerLifetimeDays": [0, 50, 500],
            }
        )

    def test_output_shape_columns_and_customer_alignment(self) -> None:
        result = preprocess_customer_features(self.customers, "standard")
        output = result.to_dataframe()
        self.assertEqual(len(output), len(self.customers))
        self.assertEqual(output.columns.tolist(), ["CustomerID", *PRIMARY_FEATURES])
        self.assertListEqual(output["CustomerID"].tolist(), [30, 10, 20])

    def test_output_has_no_nan_or_infinite_values(self) -> None:
        result = preprocess_customer_features(self.customers, "log_robust")
        self.assertFalse(result.matrix.isna().any().any())
        self.assertTrue(np.isfinite(result.matrix.to_numpy()).all())

    def test_log1p_is_applied_only_to_intended_features(self) -> None:
        result = preprocess_customer_features(self.customers, "log_standard")
        expected_input = self.customers.loc[:, PRIMARY_FEATURES].copy()
        expected_input[["Frequency", "MonetaryValue", "UniqueProducts"]] = np.log1p(
            expected_input[["Frequency", "MonetaryValue", "UniqueProducts"]]
        )
        expected = StandardScaler().fit_transform(expected_input)
        np.testing.assert_allclose(result.matrix.to_numpy(), expected)

    def test_standard_strategy_has_approximately_zero_means(self) -> None:
        result = preprocess_customer_features(self.customers, "standard")
        np.testing.assert_allclose(result.matrix.mean().to_numpy(), 0.0, atol=1e-12)

    def test_invalid_feature_name_raises_clear_error(self) -> None:
        with self.assertRaisesRegex(
            PreprocessingValidationError, "Missing required columns: NotAFeature"
        ):
            preprocess_customer_features(
                self.customers, "standard", features=["NotAFeature"]
            )

    def test_nonnumeric_feature_raises_clear_error(self) -> None:
        with self.assertRaisesRegex(
            PreprocessingValidationError, "Clustering features must be numeric"
        ):
            preprocess_customer_features(
                self.customers, "standard", features=["Country"]
            )

    def test_negative_log_feature_raises_clear_error(self) -> None:
        invalid = self.customers.copy()
        invalid.loc[0, "Frequency"] = -1
        with self.assertRaisesRegex(
            PreprocessingValidationError, "log1p features must be nonnegative"
        ):
            preprocess_customer_features(invalid, "log_standard")

    def test_missing_and_infinite_inputs_are_rejected(self) -> None:
        missing = self.customers.copy()
        missing.loc[0, "Recency"] = np.nan
        with self.assertRaisesRegex(PreprocessingValidationError, "missing values"):
            preprocess_customer_features(missing, "standard")

        infinite = self.customers.copy()
        infinite["Recency"] = infinite["Recency"].astype(float)
        infinite.loc[0, "Recency"] = np.inf
        with self.assertRaisesRegex(PreprocessingValidationError, "infinite values"):
            preprocess_customer_features(infinite, "standard")

    def test_input_dataframe_is_not_modified(self) -> None:
        original = self.customers.copy(deep=True)
        preprocess_customer_features(self.customers, "log_standard")
        pd.testing.assert_frame_equal(self.customers, original)


if __name__ == "__main__":
    unittest.main()
