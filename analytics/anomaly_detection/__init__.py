"""Anomaly detection and trend extraction subpackage."""
from analytics.anomaly_detection.detector import (
    run_anomaly_pipeline,
    compute_moving_averages,
    analyze_trends,
    detect_threshold_breaches,
    detect_statistical_anomalies,
)

__all__ = [
    "run_anomaly_pipeline",
    "compute_moving_averages",
    "analyze_trends",
    "detect_threshold_breaches",
    "detect_statistical_anomalies",
]
