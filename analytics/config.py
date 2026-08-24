"""
Configuration file for Pump P-101 Industrial Sensor Data Analytics.
Contains baseline operating thresholds, moving average parameters,
weights for health score calculation, and system limitations.
"""

from typing import Dict, Any

# Target Equipment
DEFAULT_EQUIPMENT_ID: str = "Pump P-101"

# Required Columns in Sensor Telemetry
REQUIRED_COLUMNS = [
    "timestamp",
    "pump_id",
    "vibration",
    "temperature",
    "pressure",
    "rpm",
    "flow_rate",
]

# Numeric Telemetry Columns to Analyze
SENSOR_COLUMNS = ["vibration", "temperature", "pressure", "rpm", "flow_rate"]

# Moving Average Window Size
DEFAULT_MA_WINDOW: int = 10

# Statistical Anomaly Detection (Z-score threshold)
Z_SCORE_THRESHOLD: float = 2.5

# Configurable Sensor Thresholds (Warning & Critical limits)
# Based on ISO 10816 vibration guidelines and industrial centrifugal pump standards
SENSOR_THRESHOLDS: Dict[str, Dict[str, Any]] = {
    "vibration": {
        "unit": "mm/s",
        "description": "Overall vibration RMS",
        "normal_max": 3.5,
        "warning_max": 4.5,
        "critical_max": 7.0,
        "type": "upper_bound",  # Higher value indicates degradation
    },
    "temperature": {
        "unit": "°C",
        "description": "Bearing temperature",
        "normal_max": 65.0,
        "warning_max": 75.0,
        "critical_max": 85.0,
        "type": "upper_bound",  # Higher value indicates overheating
    },
    "pressure": {
        "unit": "bar",
        "description": "Discharge pressure",
        "normal_min": 5.5,
        "normal_max": 7.0,
        "warning_min": 4.8,
        "warning_max": 7.5,
        "critical_min": 3.8,
        "critical_max": 8.5,
        "type": "range",  # Both low (loss of prime/cavitation) and high (choked discharge) are bad
    },
    "flow_rate": {
        "unit": "m³/h",
        "description": "Pump discharge flow rate",
        "normal_min": 100.0,
        "normal_max": 130.0,
        "warning_min": 90.0,
        "warning_max": 140.0,
        "critical_min": 75.0,
        "critical_max": 150.0,
        "type": "range",
    },
    "rpm": {
        "unit": "RPM",
        "description": "Motor rotational speed",
        "normal_min": 2900.0,
        "normal_max": 3000.0,
        "warning_min": 2850.0,
        "warning_max": 3050.0,
        "critical_min": 2800.0,
        "critical_max": 3100.0,
        "type": "range",
    },
}

# Component Penalty Weights for Health Scoring (sum = 1.0)
HEALTH_WEIGHTS: Dict[str, float] = {
    "vibration": 0.35,    # Strongest indicator of mechanical imbalance/bearing failure
    "temperature": 0.30,  # Critical indicator of thermal stress & lubrication failure
    "pressure": 0.20,     # Hydraulic performance indicator
    "flow_rate": 0.15,    # Process output indicator
}

# Risk Level Classification Bands
RISK_LEVEL_BANDS = [
    {
        "level": "low",
        "min_score": 85.0,
        "description": "Sensor telemetry within nominal baseline parameters. Routine monitoring recommended.",
    },
    {
        "level": "medium",
        "min_score": 65.0,
        "description": "Minor sensor deviations detected. Routine monitoring and planned inspection during next maintenance window recommended.",
    },
    {
        "level": "high",
        "min_score": 40.0,
        "description": "Significant sensor deviations detected. Engineering assessment and physical inspection recommended.",
    },
    {
        "level": "critical",
        "min_score": 0.0,
        "description": "Multiple critical sensor threshold breaches detected. Immediate operational review and physical inspection are recommended according to site procedures.",
    },
]

# System Disclaimers and Limitations
SYSTEM_LIMITATIONS = [
    "Sensor-only analysis cannot confirm physical component failure.",
    "The system provides decision support and does not guarantee equipment failure prediction.",
    "Synthetic demo data thresholds are configured for Pump P-101 baseline demonstration.",
    "Operational decisions should combine model outputs with on-site physical inspection and OEM specifications.",
]
