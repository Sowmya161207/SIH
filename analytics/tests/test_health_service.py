"""
Unit & Integration Tests for Equipment Health Service & Backend API Interface.
SIH 26117.
"""

import json
import unittest
from pathlib import Path
import pandas as pd
import numpy as np

from analytics import (
    EquipmentHealthService,
    get_equipment_health,
    STATUS_HEALTHY,
    STATUS_WARNING,
    STATUS_CRITICAL,
    EQUIPMENT_STATUS_OPTIONS,
)
from analytics.data.generate_demo_data import generate_pump_p101_data


class TestEquipmentHealthService(unittest.TestCase):
    """Test suite covering backend equipment health APIs, schemas, status mapping, and explainability."""

    @classmethod
    def setUpClass(cls):
        cls.workspace_root = Path(__file__).resolve().parent.parent.parent
        cls.sample_csv = cls.workspace_root / "data" / "raw" / "pump_p101_sensor_data.csv"
        
        # Ensure sample CSV exists
        if not cls.sample_csv.exists():
            generate_pump_p101_data(n_records=220, output_path=str(cls.sample_csv), seed=42)

        # Pristine baseline dataset
        start = pd.Timestamp("2026-08-20 06:00:00")
        cls.pristine_df = pd.DataFrame({
            "timestamp": [str(start + pd.Timedelta(minutes=5 * i)) for i in range(50)],
            "pump_id": "P-101",
            "vibration": np.random.normal(2.2, 0.05, 50).round(2),
            "temperature": np.random.normal(58.0, 0.5, 50).round(2),
            "pressure": np.random.normal(6.2, 0.05, 50).round(2),
            "rpm": np.random.normal(2950.0, 2.0, 50).round(1),
            "flow_rate": np.random.normal(115.0, 1.0, 50).round(2),
        })

    def test_01_backend_summary_schema_exact(self):
        """Verify summary output contains exact backend-expected keys and types."""
        summary = EquipmentHealthService.get_health_summary(self.sample_csv, equipment_id="P-101")
        
        # Verify required top-level keys
        expected_keys = [
            "equipment_id",
            "health_score",
            "status",
            "risk_level",
            "issues",
            "metrics",
            "recommendations",
        ]
        for k in expected_keys:
            self.assertIn(k, summary, f"Missing required key: {k}")

        self.assertEqual(summary["equipment_id"], "P-101")
        self.assertIsInstance(summary["health_score"], (int, float))
        self.assertIn(summary["status"], EQUIPMENT_STATUS_OPTIONS)
        self.assertIn(summary["risk_level"], ["low", "medium", "high", "critical"])
        self.assertIsInstance(summary["issues"], list)
        self.assertIsInstance(summary["metrics"], dict)
        self.assertIsInstance(summary["recommendations"], list)

        # Verify JSON serializability
        serialized = json.dumps(summary)
        self.assertIsInstance(serialized, str)

    def test_02_snapshot_warning_telemetry(self):
        """Verify single snapshot with elevated temperature and vibration yields 'warning' status."""
        snapshot = {
            "vibration": 4.8,      # Warning threshold is 4.5
            "temperature": 78.5,   # Warning threshold is 75.0
            "pressure": 5.9,       # Normal
            "rpm": 2948.0,         # Normal
            "flow_rate": 112.0,    # Normal
        }
        res = EquipmentHealthService.get_health_summary(snapshot, equipment_id="P-101")

        self.assertEqual(res["equipment_id"], "P-101")
        self.assertEqual(res["status"], STATUS_WARNING)
        self.assertIn(res["risk_level"], ["medium", "high"])
        self.assertLess(res["health_score"], 80.0)
        self.assertGreaterEqual(res["health_score"], 50.0)

        # Check issues and recommendations explainability
        issues_text = " ".join(res["issues"]).lower()
        self.assertTrue("temperature" in issues_text or "vibration" in issues_text)
        self.assertGreater(len(res["recommendations"]), 0)

    def test_03_snapshot_critical_telemetry(self):
        """Verify single snapshot with critical vibration yields 'critical' status."""
        critical_snapshot = {
            "vibration": 8.7,      # Exceeds 7.0 critical limit
            "temperature": 86.0,   # Exceeds 85.0 critical limit
            "pressure": 3.6,       # Below 3.8 critical min
            "rpm": 2940.0,
            "flow_rate": 70.0,     # Below 75.0 critical min
        }
        res = EquipmentHealthService.get_health_summary(critical_snapshot, equipment_id="P-101")

        self.assertEqual(res["equipment_id"], "P-101")
        self.assertEqual(res["status"], STATUS_CRITICAL)
        self.assertEqual(res["risk_level"], "critical")
        self.assertLess(res["health_score"], 50.0)

        # Must recommend SOP Section 9 or physical inspection
        recs_text = " ".join(res["recommendations"])
        self.assertTrue("SOP Section 9" in recs_text or "inspection" in recs_text.lower())

    def test_04_pristine_healthy_telemetry(self):
        """Verify pristine telemetry yields 'healthy' status, high health score, and low risk."""
        res = EquipmentHealthService.get_health_summary(self.pristine_df, equipment_id="P-101")

        self.assertEqual(res["status"], STATUS_HEALTHY)
        self.assertEqual(res["risk_level"], "low")
        self.assertGreaterEqual(res["health_score"], 85.0)
        self.assertIn("nominal", res["issues"][0].lower())

    def test_05_full_assessment_intelligence(self):
        """Verify get_full_assessment returns trends, failure modes, threshold violations, and chart series."""
        full_res = EquipmentHealthService.get_full_assessment(self.sample_csv, equipment_id="P-101")

        self.assertIn("threshold_violations", full_res)
        self.assertIn("trends", full_res)
        self.assertIn("failure_modes", full_res)
        self.assertIn("chart_data", full_res)
        self.assertIn("limitations", full_res)

        # Verify failure mode grounding
        modes = [m["failure_mode"] for m in full_res["failure_modes"]]
        self.assertTrue(any("Bearing" in m for m in modes))

    def test_06_convenience_function_get_equipment_health(self):
        """Verify get_equipment_health wrapper works in both summary and full modes."""
        summary = get_equipment_health(self.sample_csv, equipment_id="P-101", mode="summary")
        self.assertIn("health_score", summary)
        self.assertIn("status", summary)
        self.assertNotIn("chart_data", summary)  # Summary mode is concise

        full = get_equipment_health(self.sample_csv, equipment_id="P-101", mode="full")
        self.assertIn("chart_data", full)
        self.assertIn("failure_modes", full)


if __name__ == "__main__":
    unittest.main()
