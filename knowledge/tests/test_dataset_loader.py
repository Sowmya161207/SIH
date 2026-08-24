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


if __name__ == "__main__":
    unittest.main()
