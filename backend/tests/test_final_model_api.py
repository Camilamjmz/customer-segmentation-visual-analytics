import json
import unittest
from pathlib import Path

import numpy as np
import pandas as pd
from fastapi.testclient import TestClient

from app.main import app
from app.services.final_model import build_final_artifacts


class FinalModelApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root = Path(__file__).resolve().parents[2]
        cls.data = pd.read_csv(cls.root / "data/final/final_customer_segments.csv")
        cls.client = TestClient(app)

    def test_final_csv_integrity(self):
        self.assertEqual(len(self.data), 5878)
        self.assertEqual(self.data.CustomerID.nunique(), 5878)
        self.assertEqual(self.data.SegmentID.nunique(), 3)
        self.assertFalse(self.data.SegmentName.isna().any())
        self.assertEqual(self.data.groupby("SegmentID").size().sum(), 5878)

    def test_generation_is_reproducible(self):
        generated, _ = build_final_artifacts(self.root)
        pd.testing.assert_frame_equal(self.data, generated, check_dtype=False)

    def test_overview_and_model_values(self):
        overview = self.client.get("/api/overview")
        self.assertEqual(overview.status_code, 200)
        self.assertEqual(overview.json()["final_customer_count"], 5878)
        self.assertEqual(overview.json()["original_transaction_count"], 1067371)
        model = self.client.get("/api/model").json()
        self.assertAlmostEqual(model["evaluation_metrics"]["silhouette_score"], 0.31104915168375646)
        self.assertAlmostEqual(model["evaluation_metrics"]["davies_bouldin_score"], 1.1229671800563585)

    def test_segments_and_details(self):
        response = self.client.get("/api/segments")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 3)
        self.assertEqual(self.client.get("/api/segments/0").status_code, 200)
        self.assertEqual(self.client.get("/api/segments/99").status_code, 404)

    def test_customer_filtering_and_pagination(self):
        filtered = self.client.get("/api/customers", params={"segment_id": 2, "limit": 25}).json()
        self.assertEqual(len(filtered["customers"]), 25)
        self.assertTrue(all(row["SegmentID"] == 2 for row in filtered["customers"]))
        first = self.client.get("/api/customers", params={"limit": 2, "offset": 0}).json()
        second = self.client.get("/api/customers", params={"limit": 2, "offset": 2}).json()
        self.assertNotEqual(first["customers"][0]["CustomerID"], second["customers"][0]["CustomerID"])

    def test_json_endpoints_contain_only_finite_numbers(self):
        for path in ["/api/overview", "/api/model", "/api/segments", "/api/segments/1", "/api/customers?limit=10", "/api/model/comparison", "/api/methodology"]:
            response = self.client.get(path)
            self.assertEqual(response.status_code, 200)
            payload = response.json()
            def check(value):
                if isinstance(value, float): self.assertTrue(np.isfinite(value))
                elif isinstance(value, dict):
                    for child in value.values(): check(child)
                elif isinstance(value, list):
                    for child in value: check(child)
            check(payload)


if __name__ == "__main__":
    unittest.main()
