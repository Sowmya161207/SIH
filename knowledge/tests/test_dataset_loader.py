import unittest
from knowledge.datasets.metropt_loader import MetroPTDatasetLoader
from verification.verifier import verify_claims
from knowledge.retriever import search_documents


class TestMetroPTDatasetLoader(unittest.TestCase):
    def setUp(self):
        self.loader = MetroPTDatasetLoader()

    def test_load_records(self):
        """Test loading MetroPT CSV records."""
        self.assertGreater(len(self.loader.records), 0)

    def test_summary_statistics(self):
        """Test computation of telemetry summary statistics."""
        stats = self.loader.get_summary_statistics()
        self.assertIn("total_samples", stats)
        self.assertIn("vibration_rms_max", stats)
        self.assertGreater(stats["vibration_rms_max"], 4.5)
        self.assertIn("Bearing Degradation", stats["detected_failure_modes"])

    def test_sensor_evidence_to_verification_pipeline(self):
        """Test extracting sensor evidence from telemetry and running verification."""
        findings = self.loader.generate_sensor_evidence_findings()
        self.assertGreater(len(findings), 0)

        first_finding = findings[0]
        # Retrieve RAG OEM documentation for the equipment
        search_res = search_documents(first_finding["hypothesis"], filters={"equipment_tag": first_finding["equipment_tag"]})
        rag_evidence = search_res.get_evidence_texts()

        combined_evidence = first_finding["sensor_evidence"] + rag_evidence
        verification_res = verify_claims(first_finding["hypothesis"], combined_evidence)

        self.assertIn(verification_res["status"], ["SUPPORTED", "INFERRED"])
        self.assertGreater(len(verification_res["supporting_evidence"]), 0)


    def test_synthetic_telemetry_generator(self):
        """Test generating synthetic telemetry stream with injected faults."""
        from knowledge.datasets.mock_synthetic_generator import generate_synthetic_telemetry
        records = generate_synthetic_telemetry(num_samples=30, inject_anomaly_at_index=20, anomaly_type="bearing_degradation")
        self.assertEqual(len(records), 30)
        self.assertEqual(records[0]["anomaly_flag"], 0)
        self.assertEqual(records[-1]["anomaly_flag"], 1)
        self.assertEqual(records[-1]["failure_label"], "Bearing Degradation")
        self.assertGreater(records[-1]["vibration_rms_mms"], records[0]["vibration_rms_mms"])

    def test_mock_datasets_exist(self):
        """Verify presence and validity of mock telemetry and maintenance datasets."""
        import os
        import json
        telemetry_path = os.path.join(os.path.dirname(__file__), "..", "datasets", "mock_sensor_telemetry_stream.json")
        maint_path = os.path.join(os.path.dirname(__file__), "..", "datasets", "mock_maintenance_records.json")

        self.assertTrue(os.path.exists(telemetry_path))
        self.assertTrue(os.path.exists(maint_path))

        with open(telemetry_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            self.assertGreater(len(data), 0)
            self.assertIn("parameters", data[0])

        with open(maint_path, "r", encoding="utf-8") as f:
            maint_data = json.load(f)
            self.assertGreater(len(maint_data), 0)
            self.assertIn("work_order_id", maint_data[0])


if __name__ == "__main__":
    unittest.main()
