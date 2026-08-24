import unittest
from verification.claim_extraction import extract_claims, detect_modality, clean_claim_text
from verification.schemas import ClaimModality


class TestClaimExtraction(unittest.TestCase):
    def test_single_string_extraction(self):
        claims = extract_claims("Possible bearing degradation.")
        self.assertEqual(len(claims), 1)
        self.assertEqual(claims[0].text, "Possible bearing degradation.")
        self.assertEqual(claims[0].modality, ClaimModality.PROBABILISTIC)
        self.assertIn("bearing", claims[0].entities)

    def test_multiline_findings(self):
        findings = """
        Finding 1: Vibration increased 35% in Pump P-101
        - Possible bearing degradation
        3. Recommend immediate seal inspection
        """
        claims = extract_claims(findings)
        self.assertEqual(len(claims), 3)
        self.assertEqual(claims[0].text, "Vibration increased 35% in Pump P-101")
        self.assertEqual(claims[0].modality, ClaimModality.DEFINITE)
        self.assertIn("P-101", claims[0].entities)

        self.assertEqual(claims[1].modality, ClaimModality.PROBABILISTIC)
        self.assertEqual(claims[2].modality, ClaimModality.RECOMMENDATION)

    def test_list_of_dicts_extraction(self):
        data = [
            {"finding": "Motor temperature reached 130°C", "type": "sensor"},
            {"claim": "Suspected lubrication failure", "type": "rag"}
        ]
        claims = extract_claims(data)
        self.assertEqual(len(claims), 2)
        self.assertEqual(claims[0].modality, ClaimModality.DEFINITE)
        self.assertEqual(claims[1].modality, ClaimModality.PROBABILISTIC)

    def test_clean_claim_text(self):
        self.assertEqual(clean_claim_text("Finding: Bearing is worn out."), "Bearing is worn out.")
        self.assertEqual(clean_claim_text("- 1. Vibration alert"), "Vibration alert")


if __name__ == "__main__":
    unittest.main()
