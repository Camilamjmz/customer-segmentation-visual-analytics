import unittest

import numpy as np
from fastapi.testclient import TestClient

from app.main import app


class AnalyticsEndpointTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def assert_finite_json(self, value):
        if isinstance(value, float):
            self.assertTrue(np.isfinite(value))
        elif isinstance(value, dict):
            for child in value.values(): self.assert_finite_json(child)
        elif isinstance(value, list):
            for child in value: self.assert_finite_json(child)

    def test_dataset_endpoint_uses_verified_counts(self):
        response = self.client.get("/api/dataset")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["raw_transaction_count"], 1067371)
        self.assertEqual(data["cleaned_transaction_count"], 779425)
        self.assertEqual(sum(data["removed_records_by_reason"].values()), 287946)
        self.assertEqual(data["final_customer_count"], 5878)
        self.assertEqual(len(data["workbook_sheet_summary"]), 2)
        self.assertEqual(len(data["customer_feature_dictionary"]), 10)

    def test_distribution_endpoints_for_all_allowed_features(self):
        allowed = ["Recency", "Frequency", "MonetaryValue", "UniqueProducts", "CustomerLifetimeDays"]
        for feature in allowed:
            response = self.client.get("/api/eda/distributions", params={"feature": feature})
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertEqual(data["count"], 5878)
            self.assertEqual(sum(data["histogram"]["counts"]), 5878)
            self.assertEqual(data["log1p_histogram"] is not None, feature in {"Frequency", "MonetaryValue", "UniqueProducts"})
            self.assert_finite_json(data)
        self.assertEqual(self.client.get("/api/eda/distributions", params={"feature": "Country"}).status_code, 422)

    def test_correlations_are_square_symmetric_and_finite(self):
        data = self.client.get("/api/eda/correlations").json()
        matrix = np.asarray(data["matrix"])
        self.assertEqual(matrix.shape, (len(data["features"]), len(data["features"])))
        np.testing.assert_allclose(matrix, matrix.T)
        np.testing.assert_allclose(np.diag(matrix), 1)
        self.assertGreater(len(data["strongest_correlation_pairs"]), 0)
        self.assert_finite_json(data)

    def test_outlier_endpoint_covers_all_numeric_features(self):
        response = self.client.get("/api/eda/outliers")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data["features"]), 8)
        for feature in data["features"]:
            self.assertGreaterEqual(feature["outlier_count"], 0)
            self.assertLessEqual(len(feature["representative_extreme_customers"]), 3)
        self.assert_finite_json(data)

    def test_segment_distributions_cover_three_segments_and_eight_features(self):
        response = self.client.get("/api/segments/distributions")
        self.assertEqual(response.status_code, 200)
        segments = response.json()["segments"]
        self.assertEqual(len(segments), 3)
        self.assertEqual(sum(segment["customer_count"] for segment in segments), 5878)
        self.assertTrue(all(len(segment["features"]) == 8 for segment in segments))
        self.assert_finite_json(response.json())

    def test_model_validation_returns_verified_candidate_evidence(self):
        response = self.client.get("/api/model/validation")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["recommended_k"], 3)
        self.assertEqual([item["k"] for item in data["candidates"]], [3, 4])
        self.assertAlmostEqual(data["candidates"][0]["subsampling_stability"]["mean_ari"], 0.9800658118964514)
        self.assertAlmostEqual(data["candidates"][1]["feature_sensitivity"]["ari_vs_primary"], 0.8858385957542388)
        self.assert_finite_json(data)


if __name__ == "__main__":
    unittest.main()
