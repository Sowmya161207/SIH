import unittest
from verification.verifier import verify_claims, ClaimVerifier
from verification.schemas import VerificationStatus


class TestVerifier(unittest.TestCase):
    def test_mrpl_user_example_inferred(self):
        """Test the exact SIH26117 MRPL example from requirements."""
        finding = "Possible bearing degradation."
        evidence = [
            "Vibration increased 35%",
            "Bearing inspection overdue",
            "Equipment manual lists bearing wear as a possible cause"
        ]

        result = verify_claims(finding, evidence)

        self.assertIsInstance(result, dict)
        self.assertEqual(result["claim"], "Possible bearing degradation.")
        self.assertEqual(result["status"], "INFERRED")
        self.assertEqual(result["confidence"], 0.78)
        self.assertEqual(len(result["supporting_evidence"]), 3)
        self.assertIn("Indirect evidence supports the possibility.", result["reason"])
        self.assertIn("No physical bearing inspection available.", result["limitations"])

    def test_supported_claim(self):
        """Test a definite factual claim with direct sensor evidence."""
        finding = "Vibration increased 35% on P-101"
        evidence = [
            "Vibration increased 35% on P-101 drive end",
            "Turbine speed is 1500 RPM"
        ]

        result = verify_claims(finding, evidence)
        self.assertEqual(result["status"], "SUPPORTED")
        self.assertGreaterEqual(result["confidence"], 0.85)
        self.assertEqual(len(result["supporting_evidence"]), 1)

    def test_unsupported_claim_contradiction(self):
        """Test a claim that is contradicted by maintenance inspection logs."""
        finding = "Bearing degradation detected on Pump P-101"
        evidence = [
            "Maintenance log: P-101 bearing inspected and in healthy condition with no wear found"
        ]

        result = verify_claims(finding, evidence)
        self.assertEqual(result["status"], "UNSUPPORTED")
        self.assertGreaterEqual(result["confidence"], 0.85)
        self.assertIn("Contradicted by evidence", result["reason"])

    def test_insufficient_evidence(self):
        """Test a claim where no relevant evidence is available."""
        finding = "Cooling water valve V-302 stuck open"
        evidence = [
            "Vibration increased 35% on P-101",
            "Lubrication oil level is optimal"
        ]

        result = verify_claims(finding, evidence)
        self.assertEqual(result["status"], "INSUFFICIENT_EVIDENCE")
        self.assertLessEqual(result["confidence"], 0.40)

    def test_batch_verification_with_report(self):
        """Test batch verification returning multiple results and report."""
        findings = [
            "Vibration increased 35% on P-101",
            "Possible bearing degradation.",
            "Transformer oil leak detected"
        ]
        evidence = [
            "Vibration increased 35% on P-101",
            "Bearing inspection overdue",
            "Equipment manual lists bearing wear as a possible cause"
        ]

        results = verify_claims(findings, evidence)
        self.assertIsInstance(results, list)
        self.assertEqual(len(results), 3)
        self.assertEqual(results[0]["status"], "SUPPORTED")
        self.assertEqual(results[1]["status"], "INFERRED")
        self.assertEqual(results[2]["status"], "INSUFFICIENT_EVIDENCE")

        verifier = ClaimVerifier()
        report = verifier.verify_to_report(findings, evidence)
        self.assertEqual(report.summary["SUPPORTED"], 1)
        self.assertEqual(report.summary["INFERRED"], 1)
        self.assertEqual(report.summary["INSUFFICIENT_EVIDENCE"], 1)

    def test_structured_rag_and_sensor_inputs(self):
        """Test verification with structured dictionaries representing RAG and Sensor payloads."""
        findings = [
            {"finding": "Motor temperature reached 130°C", "source": "Sensor"},
            {"claim": "Recommend bearing replacement during next scheduled turnaround", "source": "AI-Assistant"}
        ]
        evidence = [
            {"text": "Temperature sensor TE-101 reading 130°C (High Alarm)", "source": "Sensor", "confidence": 0.98},
            {"text": "RAG Manual: If bearing temperature persists > 120°C, schedule replacement", "source": "RAG"}
        ]

        results = verify_claims(findings, evidence)
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]["status"], "SUPPORTED")
        self.assertEqual(results[1]["status"], "INFERRED")

    def test_empty_findings(self):
        """Test handling of empty findings input."""
        results = verify_claims("", ["Vibration is normal"])
        self.assertEqual(results, [])


if __name__ == "__main__":
    unittest.main()
