import unittest
from verification.schemas import Claim, EvidenceItem, ClaimModality
from verification.evidence_matching import match_claim_to_evidence, check_contradiction, is_indirect_evidence


class TestEvidenceMatching(unittest.TestCase):
    def test_direct_evidence_matching(self):
        claim = Claim(
            text="Vibration increased 35%",
            modality=ClaimModality.DEFINITE,
            keywords=["vibration", "increased", "35%"],
            entities=[]
        )
        evidence = [
            EvidenceItem(text="Sensor Telemetry: Vibration increased 35% on drive end"),
            EvidenceItem(text="Ambient temperature is 32°C")
        ]
        match = match_claim_to_evidence(claim, evidence)
        self.assertTrue(len(match.direct_matches) > 0)
        self.assertFalse(match.has_contradiction)

    def test_indirect_evidence_matching(self):
        claim = Claim(
            text="Possible bearing degradation",
            modality=ClaimModality.PROBABILISTIC,
            keywords=["possible", "bearing", "degradation"],
            entities=["bearing"]
        )
        evidence = [
            EvidenceItem(text="Vibration increased 35%"),
            EvidenceItem(text="Bearing inspection overdue"),
            EvidenceItem(text="Equipment manual lists bearing wear as a possible cause")
        ]
        match = match_claim_to_evidence(claim, evidence)
        self.assertTrue(len(match.indirect_matches) >= 2)
        self.assertFalse(match.has_contradiction)

    def test_contradiction_detection(self):
        claim = Claim(
            text="Bearing failure observed in Pump P-101",
            modality=ClaimModality.DEFINITE,
            keywords=["bearing", "failure", "observed", "pump", "p-101"],
            entities=["P-101", "bearing", "pump"]
        )
        evidence = [
            EvidenceItem(text="Maintenance Log: P-101 bearing inspected, healthy condition, no wear or degradation found")
        ]
        match = match_claim_to_evidence(claim, evidence)
        self.assertTrue(match.has_contradiction)


if __name__ == "__main__":
    unittest.main()
