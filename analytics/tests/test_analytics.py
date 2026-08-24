"""
Unit and Integration Tests for Pump P-101 Data Analytics Module.
SIH26117.
"""

import json
import unittest
from pathlib import Path
import pandas as pd
import numpy as np

from analytics.config import (
    REQUIRED_COLUMNS,
    SENSOR_COLUMNS,
    SYSTEM_LIMITATIONS,
    DEFAULT_EQUIPMENT_ID,
)
from analytics.processing.validation import validate_and_prepare_data
from analytics.data.generate_demo_data import generate_pump_p101_data
from analytics.anomaly_detection.detector import (
    compute_moving_averages,
    analyze_trends,
    detect_threshold_breaches,
    detect_statistical_anomalies,
    run_anomaly_pipeline,
)
from analytics.scoring.health_score import compute_health_index
from analytics.main import analyze_sensor_data


class TestPumpP101Analytics(unittest.TestCase):
    """Test suite covering data validation, feature extraction, anomaly detection, scoring, and output schema."""

    @classmethod
    def setUpClass(cls):
        """Generate in-memory datasets for testing."""
        # Realistic synthetic dataset (normal + degradation)
        cls.demo_df = generate_pump_p101_data(n_records=220, seed=123)

        # Baseline pristine dataset (healthy only)
        start = pd.Timestamp("2026-08-20 06:00:00")
        cls.healthy_df = pd.DataFrame({
            "timestamp": [str(start + pd.Timedelta(minutes=5 * i)) for i in range(50)],
            "pump_id": DEFAULT_EQUIPMENT_ID,
            "vibration": np.random.normal(2.2, 0.1, 50).round(2),
            "temperature": np.random.normal(58.0, 0.5, 50).round(2),
            "pressure": np.random.normal(6.2, 0.05, 50).round(2),
            "rpm": np.random.normal(2950.0, 3.0, 50).round(1),
            "flow_rate": np.random.normal(115.0, 1.0, 50).round(2),
        })

    def test_01_demo_data_generation(self):
        """Verify demo data generator produces correct schema and record counts."""
        df = generate_pump_p101_data(n_records=205, seed=42)
        self.assertGreaterEqual(len(df), 200)
        for col in REQUIRED_COLUMNS:
            self.assertIn(col, df.columns)
        self.assertEqual(df["pump_id"].iloc[0], "Pump P-101")

    def test_02_validation_success_and_errors(self):
        """Verify data validation handling and error triggers."""
        # 1. Valid input returns clean DataFrame
        cleaned = validate_and_prepare_data(self.demo_df)
        self.assertIsInstance(cleaned, pd.DataFrame)
        self.assertEqual(len(cleaned), len(self.demo_df))

        # 2. Missing column raises ValueError
        invalid_df = self.demo_df.drop(columns=["vibration"])
        with self.assertRaises(ValueError) as ctx:
            validate_and_prepare_data(invalid_df)
        self.assertIn("Missing required columns", str(ctx.exception))

        # 3. Insufficient rows raises ValueError
        tiny_df = self.demo_df.iloc[:2]
        with self.assertRaises(ValueError) as ctx:
            validate_and_prepare_data(tiny_df)
        self.assertIn("Insufficient data points", str(ctx.exception))

        # 4. List of dicts ingestion
        dict_list = self.healthy_df.to_dict(orient="records")
        cleaned_from_dict = validate_and_prepare_data(dict_list)
        self.assertEqual(len(cleaned_from_dict), len(dict_list))

    def test_03_moving_averages(self):
        """Verify rolling moving averages are calculated for all sensor columns."""
        df_ma = compute_moving_averages(self.demo_df, window=5)
        for col in SENSOR_COLUMNS:
            ma_col = f"{col}_ma"
            self.assertIn(ma_col, df_ma.columns)
            self.assertFalse(df_ma[ma_col].isnull().any())

    def test_04_trend_analysis(self):
        """Verify upward vibration/temperature and downward pressure/flow trends in degraded dataset."""
        cleaned = validate_and_prepare_data(self.demo_df)
        trends = analyze_trends(cleaned)

        self.assertEqual(trends["vibration"]["direction"], "increasing")
        self.assertEqual(trends["temperature"]["direction"], "increasing")
        self.assertEqual(trends["pressure"]["direction"], "decreasing")
        self.assertEqual(trends["flow_rate"]["direction"], "decreasing")
        self.assertEqual(trends["rpm"]["direction"], "stable")

    def test_05_threshold_and_anomaly_detection(self):
        """Verify threshold breach flags and Z-score outlier detection."""
        cleaned = validate_and_prepare_data(self.demo_df)
        pipeline_res = run_anomaly_pipeline(cleaned)

        self.assertGreater(pipeline_res["total_critical_breaches"], 0)
        self.assertGreater(pipeline_res["total_warning_breaches"], 0)
        self.assertIn("vibration", pipeline_res["breach_counts"])
        self.assertGreater(pipeline_res["breach_counts"]["vibration"]["critical_breaches"], 0)

    def test_06_health_scoring_logic(self):
        """Verify health score reflects healthy vs degraded conditions."""
        # Degraded dataset must yield low health score and high/critical risk
        deg_res = run_anomaly_pipeline(validate_and_prepare_data(self.demo_df))
        deg_health = compute_health_index(deg_res)
        self.assertLess(deg_health["health_score"], 60.0)
        self.assertIn(deg_health["risk_level"], ["high", "critical"])

        # Healthy dataset must yield high health score and low risk
        healthy_res = run_anomaly_pipeline(validate_and_prepare_data(self.healthy_df))
        healthy_health = compute_health_index(healthy_res)
        self.assertGreaterEqual(healthy_health["health_score"], 85.0)
        self.assertEqual(healthy_health["risk_level"], "low")

    def test_07_analyze_sensor_data_full_output_contract(self):
        """Verify analyze_sensor_data returns exact required structure and is JSON-serializable."""
        result = analyze_sensor_data(self.demo_df)

        # Check top-level keys
        expected_keys = [
            "equipment",
            "health_score",
            "risk_level",
            "anomalies",
            "trends",
            "chart_data",
            "limitations",
        ]
        for key in expected_keys:
            self.assertIn(key, result)

        self.assertEqual(result["equipment"], "Pump P-101")
        self.assertIsInstance(result["health_score"], float)
        self.assertIn(result["risk_level"], ["low", "medium", "high", "critical"])
        self.assertIsInstance(result["chart_data"], list)
        self.assertGreater(len(result["chart_data"]), 0)

        # Verify mandatory limitations
        self.assertTrue(
            any("Sensor-only analysis cannot confirm physical component failure." in s for s in result["limitations"])
        )
        self.assertTrue(
            any("The system provides decision support and does not guarantee equipment failure prediction." in s for s in result["limitations"])
        )

        # Verify JSON serialization works without error
        serialized = json.dumps(result)
        self.assertIsInstance(serialized, str)
        self.assertGreater(len(serialized), 100)


if __name__ == "__main__":
    unittest.main()
