"""
Unit Tests for Industrial Incident Intelligence & Planner Tool Interface.
SIH PS 26117.

Validates:
1. Normal condition
2. Threshold violation
3. High-risk equipment
4. Missing data handling
5. Incident investigation
6. Explainability / evidence output (Observed vs Inference vs Recommendation separation)
"""

import unittest
from pathlib import Path

from analytics import (
    analyze_equipment,
    investigate_incident,
    predict_maintenance_risk,
    analyze_sensor_data,
)


class TestIndustrialIncidentIntelligence(unittest.TestCase):
    """Test suite for industrial incident intelligence and planner tools."""

    @classmethod
    def setUpClass(cls):
        cls.workspace_root = Path(__file__).resolve().parent.parent.parent
        cls.sample_csv = cls.workspace_root / "data" / "raw" / "pump_p101_sensor_data.csv"

    def test_01_normal_condition(self):
        """Test equipment analysis on healthy nominal telemetry."""
        nominal_telemetry = {
            "vibration": 2.2,
            "temperature": 62.0,
            "pressure": 4.2,
            "speed": 1450,
            "flow_rate": 115.0,
        }
        res = analyze_equipment(equipment_id="Pump P-101", current_telemetry=nominal_telemetry)

        self.assertEqual(res["equipment"], "Pump P-101")
        self.assertEqual(res["risk_level"], "LOW")
        self.assertEqual(len(res["anomalies"]), 0)
        self.assertGreater(len(res["triplet_insights"]), 0)
        self.assertIn("nominal", res["triplet_insights"][0]["observed"].lower())

    def test_02_threshold_violation(self):
        """Test detection and grounding of warning and critical threshold violations."""
        # Critical vibration breach
        critical_telemetry = {
            "vibration": 8.7,
            "temperature": 71.0,
            "pressure": 4.1,
            "speed": 1450,
        }
        res = analyze_equipment(equipment_id="Pump P-101", current_telemetry=critical_telemetry)

        self.assertGreater(len(res["anomalies"]), 0)
        vib_anomaly = next((a for a in res["anomalies"] if a["sensor"] == "vibration"), None)
        self.assertIsNotNone(vib_anomaly)
        self.assertEqual(vib_anomaly["condition"], "CRITICAL")
        self.assertEqual(vib_anomaly["evidence_source"]["document"], "Pump_P101_Equipment_Manual.pdf")
        self.assertEqual(vib_anomaly["evidence_source"]["page"], 2)

    def test_03_high_risk_equipment(self):
        """Test predictive maintenance risk on degraded historical dataset."""
        res = predict_maintenance_risk(equipment_id="Pump P-101", sensor_data=self.sample_csv)

        self.assertEqual(res["equipment"], "Pump P-101")
        self.assertEqual(res["overall_maintenance_risk"], "CRITICAL")
        self.assertLess(res["health_index"], 40.0)
        self.assertEqual(res["urgency"], "IMMEDIATE_OPERATIONAL_REVIEW")
        self.assertGreater(len(res["failure_mode_indicators"]), 0)
        
        # Verify failure mode grounding
        bearing_indicator = next(
            (f for f in res["failure_mode_indicators"] if "Bearing" in f["failure_mode"]), None
        )
        self.assertIsNotNone(bearing_indicator)
        self.assertIn("Pump_P101_Equipment_Manual.pdf", bearing_indicator["evidence_basis"]["document"])

    def test_04_missing_data_handling(self):
        """Test graceful degradation when no telemetry data is supplied."""
        res = analyze_equipment(equipment_id="Pump P-101", sensor_data=None, current_telemetry=None)

        self.assertEqual(res["equipment"], "Pump P-101")
        self.assertEqual(res["status"], "DATA_UNAVAILABLE")
        self.assertEqual(res["risk_level"], "UNKNOWN")
        self.assertIsNone(res["health_score"])
        self.assertGreater(len(res["triplet_insights"]), 0)
        self.assertIn("unverified", res["triplet_insights"][0]["inference"].lower())

    def test_05_incident_investigation(self):
        """Test deterministic incident investigation on canonical event INC-P101-2026-007."""
        res = investigate_incident(incident_id="INC-P101-2026-007", equipment_id="Pump P-101")

        self.assertEqual(res["incident_id"], "INC-P101-2026-007")
        self.assertEqual(res["severity"], "HIGH")
        self.assertEqual(res["incident_date"], "21 July 2026")
        
        # Verify root causes
        causes = [c["cause"] for c in res["suspected_root_causes"]]
        self.assertIn("Bearing Degradation", causes)
        self.assertIn("Coupling Misalignment", causes)

        # Verify before/after measurements
        measurements = res["before_and_after_measurements"]
        self.assertEqual(measurements["vibration"]["before"], "8.7 mm/s RMS")
        self.assertEqual(measurements["vibration"]["after"], "2.6 mm/s RMS")
        self.assertEqual(measurements["vibration"]["status"], "RESTORED_NORMAL")

    def test_06_explainability_and_evidence_triplets(self):
        """Verify strict 3-part separation: Observed (fact) vs Inference (hypothesis) vs Recommendation (action)."""
        critical_telemetry = {"vibration": 8.7, "temperature": 78.0, "pressure": 3.6}
        res = analyze_equipment(equipment_id="Pump P-101", current_telemetry=critical_telemetry)

        triplets = res.get("triplet_insights", [])
        self.assertGreater(len(triplets), 0)

        for t in triplets:
            self.assertIn("observed", t)
            self.assertIn("inference", t)
            self.assertIn("recommendation", t)
            self.assertIsInstance(t["observed"], str)
            self.assertIsInstance(t["inference"], str)
            self.assertIsInstance(t["recommendation"], str)
            
            # Verify inference is cautious (contains probabilistic phrasing)
            self.assertTrue(
                any(w in t["inference"].lower() for w in ["may", "indicate", "associated", "consistent", "deviation", "unverified"])
            )


if __name__ == "__main__":
    unittest.main()
