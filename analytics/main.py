"""
Main Entry Point for Pump P-101 Data Analytics Module.
SIH26117 - Smart India Hackathon.

Exposes `analyze_sensor_data(data)` which orchestrates data validation,
moving averages, trend identification, anomaly & threshold breach detection,
equipment health scoring, risk classification, and chart-ready serialization.
"""

from typing import Union, List, Dict, Any, Optional
from pathlib import Path
import json
import pandas as pd
import numpy as np

from analytics.config import (
    DEFAULT_EQUIPMENT_ID,
    SENSOR_COLUMNS,
    DEFAULT_MA_WINDOW,
    Z_SCORE_THRESHOLD,
    SYSTEM_LIMITATIONS,
)
from analytics.processing.validation import validate_and_prepare_data
from analytics.anomaly_detection.detector import run_anomaly_pipeline
from analytics.scoring.health_score import compute_health_index


def _to_json_serializable(obj: Any) -> Any:
    """
    Recursively converts numpy types, pandas Timestamps, and float NaNs
    to standard JSON-compliant Python primitives.
    """
    if isinstance(obj, dict):
        return {str(k): _to_json_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_to_json_serializable(v) for v in obj]
    elif isinstance(obj, tuple):
        return [_to_json_serializable(v) for v in obj]
    elif isinstance(obj, (np.int_, np.intc, np.intp, np.int8, np.int16, np.int32, np.int64,
                          np.uint8, np.uint16, np.uint32, np.uint64)):
        return int(obj)
    elif isinstance(obj, (np.float16, np.float32, np.float64)):
        if np.isnan(obj) or np.isinf(obj):
            return None
        return float(obj)
    elif isinstance(obj, (np.bool_, bool)):
        return bool(obj)
    elif isinstance(obj, (pd.Timestamp, np.datetime64)):
        return str(obj)
    elif pd.isna(obj):
        return None
    return obj


def format_chart_data(df_processed: pd.DataFrame) -> List[Dict[str, Any]]:
    """
    Converts processed telemetry into clean time-series records
    optimized for frontend charting libraries (Chart.js, Recharts, ECharts).
    """
    chart_records = []
    
    for _, row in df_processed.iterrows():
        record: Dict[str, Any] = {
            "timestamp": str(row["timestamp"]),
        }
        
        for col in SENSOR_COLUMNS:
            record[col] = round(float(row[col]), 2) if pd.notna(row[col]) else None
            record[f"{col}_ma"] = (
                round(float(row[f"{col}_ma"]), 2) if f"{col}_ma" in row and pd.notna(row[f"{col}_ma"]) else None
            )
            record[f"{col}_warning"] = bool(row.get(f"{col}_warning", False))
            record[f"{col}_critical"] = bool(row.get(f"{col}_critical", False))
            record[f"{col}_anomaly"] = bool(row.get(f"{col}_is_anomaly", False))
            
        chart_records.append(record)
        
    return chart_records


def analyze_sensor_data(
    data: Union[pd.DataFrame, List[Dict[str, Any]], Dict[str, List[Any]], str, Path],
    ma_window: int = DEFAULT_MA_WINDOW,
    z_threshold: float = Z_SCORE_THRESHOLD,
) -> Dict[str, Any]:
    """
    Analyzes industrial sensor telemetry for Pump P-101.

    Workflow:
    ---------
    1. Validates schema and prepares time-series data.
    2. Calculates rolling moving averages.
    3. Detects directional trends (increasing/decreasing/stable) with slopes.
    4. Detects statistical outliers using explainable Z-scores.
    5. Identifies threshold breaches (warning and critical limits).
    6. Calculates an explainable 0–100 equipment health index.
    7. Classifies overall risk (low, medium, high, critical).
    8. Formats chart-ready time-series records.
    9. Returns a 100% JSON-serializable output structure.

    Parameters:
    -----------
    data : pd.DataFrame | list[dict] | dict[str, list] | str | Path
        Raw sensor readings or path to CSV file.
    ma_window : int, default=10
        Moving average rolling window size.
    z_threshold : float, default=2.5
        Z-score threshold for statistical outlier detection.

    Returns:
    --------
    dict with keys:
        - equipment: str (e.g. 'Pump P-101')
        - health_score: float (0.0 - 100.0)
        - risk_level: str ('low' | 'medium' | 'high' | 'critical')
        - risk_description: str
        - health_breakdown: dict (sensor subscores and primary drivers)
        - anomalies: dict (counts, per-sensor breakdown, latest active events)
        - trends: dict (direction, slope, baseline/latest means, interpretation)
        - chart_data: list of dicts (timestamps, raw values, MAs, breach flags)
        - limitations: list of str (mandatory disclaimers)
    """
    # 1. Validate & prepare data
    df_clean = validate_and_prepare_data(data)
    equipment_id = str(df_clean["pump_id"].iloc[0]) if "pump_id" in df_clean.columns else DEFAULT_EQUIPMENT_ID

    # 2. Run Anomaly Detection Pipeline (MAs, Trends, Breaches, Z-Scores)
    anomaly_results = run_anomaly_pipeline(
        df_clean, ma_window=ma_window, z_threshold=z_threshold
    )

    # 3. Calculate Health Score and Risk Classification
    health_results = compute_health_index(anomaly_results)

    # 4. Generate Chart-Ready Time Series
    chart_data = format_chart_data(anomaly_results["processed_df"])

    # 5. Assemble structured anomalies summary
    total_stat_outliers = sum(
        b["statistical_outliers"] for b in anomaly_results["breach_counts"].values()
    )
    
    anomalies_summary = {
        "summary": (
            f"Detected {anomaly_results['total_critical_breaches']} critical breaches, "
            f"{anomaly_results['total_warning_breaches']} warning breaches, and "
            f"{total_stat_outliers} statistical outliers."
        ),
        "total_critical_breaches": anomaly_results["total_critical_breaches"],
        "total_warning_breaches": anomaly_results["total_warning_breaches"],
        "total_statistical_outliers": total_stat_outliers,
        "by_sensor": anomaly_results["breach_counts"],
        "latest_events": anomaly_results["latest_events"],
    }

    # 6. Assemble Final Analytics Output
    output: Dict[str, Any] = {
        "equipment": equipment_id,
        "health_score": health_results["health_score"],
        "risk_level": health_results["risk_level"],
        "risk_description": health_results["risk_description"],
        "health_breakdown": {
            "sensor_subscores": health_results["sensor_subscores"],
            "primary_drivers": health_results["primary_drivers"],
        },
        "anomalies": anomalies_summary,
        "trends": anomaly_results["trends"],
        "chart_data": chart_data,
        "limitations": SYSTEM_LIMITATIONS,
    }

    # 7. Ensure 100% JSON serializable
    return _to_json_serializable(output)


if __name__ == "__main__":
    # Self-test demo using synthetic dataset
    workspace_root = Path(__file__).resolve().parent.parent
    sample_csv = workspace_root / "data" / "raw" / "pump_p101_sensor_data.csv"

    if not sample_csv.exists():
        print(f"Generating sample dataset at {sample_csv}...")
        from analytics.data.generate_demo_data import generate_pump_p101_data
        generate_pump_p101_data(output_path=str(sample_csv))

    print(f"Running analyze_sensor_data on {sample_csv}...")
    results = analyze_sensor_data(sample_csv)
    print("\n--- ANALYTICS SUMMARY ---")
    print(f"Equipment    : {results['equipment']}")
    print(f"Health Score : {results['health_score']} / 100")
    print(f"Risk Level   : {results['risk_level'].upper()}")
    print(f"Drivers      : {results['health_breakdown']['primary_drivers']}")
    print(f"Chart Points : {len(results['chart_data'])} records")
    print(f"JSON Test    : Serialized successfully ({len(json.dumps(results))} bytes)")
