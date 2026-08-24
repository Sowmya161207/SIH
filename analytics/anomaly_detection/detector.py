"""
Anomaly detection and trend analysis module for Pump P-101 sensor telemetry.
Provides explainable statistical anomaly detection (Z-score), moving averages,
trend slope estimation, and industrial threshold breach monitoring.
"""

from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np

from analytics.config import (
    SENSOR_COLUMNS,
    SENSOR_THRESHOLDS,
    DEFAULT_MA_WINDOW,
    Z_SCORE_THRESHOLD,
)


def compute_moving_averages(df: pd.DataFrame, window: int = DEFAULT_MA_WINDOW) -> pd.DataFrame:
    """
    Computes rolling moving averages for all numeric sensor columns.
    Uses min_periods=1 to provide moving averages from the first observation.
    """
    df_ma = df.copy()
    for col in SENSOR_COLUMNS:
        df_ma[f"{col}_ma"] = df_ma[col].rolling(window=window, min_periods=1).mean().round(3)
    return df_ma


def analyze_trends(df: pd.DataFrame, window: int = DEFAULT_MA_WINDOW) -> Dict[str, Dict[str, Any]]:
    """
    Calculates trend direction and slope for each sensor using linear regression slope
    over the telemetry series and compares the latest window against baseline.

    Returns:
    --------
    dict with metric -> {'trend': 'increasing'|'decreasing'|'stable', 'slope': float, 'summary': str}
    """
    trends = {}
    n = len(df)
    x = np.arange(n)

    for col in SENSOR_COLUMNS:
        y = df[col].values
        
        # Calculate linear slope (rate of change per sample)
        if n > 1 and np.std(x) > 0:
            slope, _ = np.polyfit(x, y, 1)
        else:
            slope = 0.0

        # Normalized slope relative to metric scale (percentage shift over entire series)
        mean_val = float(np.mean(y)) if np.mean(y) != 0 else 1.0
        total_change_pct = (float(slope) * n / abs(mean_val)) * 100.0

        # Determine direction based on normalized threshold (e.g. > 5% change over dataset)
        if total_change_pct > 5.0:
            direction = "increasing"
        elif total_change_pct < -5.0:
            direction = "decreasing"
        else:
            direction = "stable"

        # Specialized context interpretation for industrial pumps
        if col == "vibration" and direction == "increasing":
            context = "An upward vibration trend may warrant inspection for possible mechanical issues."
        elif col == "temperature" and direction == "increasing":
            context = "A rising temperature trend indicates elevated thermal conditions and may warrant inspection."
        elif col == "pressure" and direction == "decreasing":
            context = "A sustained pressure decrease indicates abnormal hydraulic behavior and may warrant further investigation."
        elif col == "flow_rate" and direction == "decreasing":
            context = "A decreasing flow rate pattern indicates reduced hydraulic throughput and may warrant inspection."
        elif col == "rpm" and direction == "stable":
            context = "Motor speed remains stable within expected grid frequency parameters."
        else:
            context = f"{col.replace('_', ' ').title()} trend is currently {direction}."

        trends[col] = {
            "direction": direction,
            "slope": round(float(slope), 4),
            "total_change_pct": round(total_change_pct, 2),
            "baseline_mean": round(float(np.mean(y[: max(5, n // 4)])), 2),
            "latest_mean": round(float(np.mean(y[-max(5, n // 4) :])), 2),
            "interpretation": context,
        }

    return trends


def detect_threshold_breaches(df: pd.DataFrame) -> pd.DataFrame:
    """
    Checks each sensor reading against defined Warning and Critical thresholds.
    Adds boolean breach columns: '{col}_warning', '{col}_critical'.
    """
    df_breaches = df.copy()

    for col in SENSOR_COLUMNS:
        thresholds = SENSOR_THRESHOLDS.get(col, {})
        t_type = thresholds.get("type", "upper_bound")

        if t_type == "upper_bound":
            warn_max = thresholds.get("warning_max", float("inf"))
            crit_max = thresholds.get("critical_max", float("inf"))
            df_breaches[f"{col}_warning"] = df_breaches[col] >= warn_max
            df_breaches[f"{col}_critical"] = df_breaches[col] >= crit_max

        elif t_type == "range":
            warn_min = thresholds.get("warning_min", float("-inf"))
            warn_max = thresholds.get("warning_max", float("inf"))
            crit_min = thresholds.get("critical_min", float("-inf"))
            crit_max = thresholds.get("critical_max", float("inf"))

            df_breaches[f"{col}_warning"] = (df_breaches[col] <= warn_min) | (
                df_breaches[col] >= warn_max
            )
            df_breaches[f"{col}_critical"] = (df_breaches[col] <= crit_min) | (
                df_breaches[col] >= crit_max
            )

    return df_breaches


def detect_statistical_anomalies(
    df: pd.DataFrame, z_threshold: float = Z_SCORE_THRESHOLD
) -> pd.DataFrame:
    """
    Detects statistical outliers using Z-score based on initial baseline (first 25% of data or mean/std).
    Adds '{col}_zscore' and '{col}_is_anomaly' columns.
    """
    df_out = df.copy()
    n = len(df_out)
    baseline_cutoff = max(10, n // 4)

    for col in SENSOR_COLUMNS:
        # Use early baseline mean and std if stable, or global mean/std
        baseline_vals = df_out[col].iloc[:baseline_cutoff]
        base_mean = baseline_vals.mean()
        base_std = baseline_vals.std()

        if base_std == 0 or np.isnan(base_std):
            base_std = 1e-6

        z_scores = (df_out[col] - base_mean) / base_std
        df_out[f"{col}_zscore"] = z_scores.round(2)
        df_out[f"{col}_is_anomaly"] = np.abs(z_scores) >= z_threshold

    return df_out


def run_anomaly_pipeline(
    df: pd.DataFrame,
    ma_window: int = DEFAULT_MA_WINDOW,
    z_threshold: float = Z_SCORE_THRESHOLD,
) -> Dict[str, Any]:
    """
    Executes the full anomaly detection pipeline:
    1. Moving average computation
    2. Threshold breach identification
    3. Statistical Z-score anomaly detection
    4. Trend analysis
    5. Summary aggregation

    Returns:
    --------
    dict containing processed DataFrame and structured anomaly summary.
    """
    df_processed = compute_moving_averages(df, window=ma_window)
    df_processed = detect_threshold_breaches(df_processed)
    df_processed = detect_statistical_anomalies(df_processed, z_threshold=z_threshold)

    trends = analyze_trends(df_processed, window=ma_window)

    # Compile explainable anomaly events
    anomaly_events: List[Dict[str, Any]] = []
    breach_counts: Dict[str, Dict[str, int]] = {}

    for col in SENSOR_COLUMNS:
        warn_count = int(df_processed[f"{col}_warning"].sum())
        crit_count = int(df_processed[f"{col}_critical"].sum())
        stat_count = int(df_processed[f"{col}_is_anomaly"].sum())

        breach_counts[col] = {
            "warning_breaches": warn_count,
            "critical_breaches": crit_count,
            "statistical_outliers": stat_count,
        }

        # Check most recent reading (latest state)
        last_row = df_processed.iloc[-1]
        timestamp_str = str(last_row["timestamp"])

        if bool(last_row.get(f"{col}_critical", False)):
            val = float(last_row[col])
            crit_max = SENSOR_THRESHOLDS[col].get("critical_max")
            crit_min = SENSOR_THRESHOLDS[col].get("critical_min")
            anomaly_events.append({
                "severity": "CRITICAL",
                "sensor": col,
                "timestamp": timestamp_str,
                "current_value": val,
                "unit": SENSOR_THRESHOLDS[col]["unit"],
                "message": f"Critical threshold breach on {col} ({val} {SENSOR_THRESHOLDS[col]['unit']}).",
            })
        elif bool(last_row.get(f"{col}_warning", False)):
            val = float(last_row[col])
            anomaly_events.append({
                "severity": "WARNING",
                "sensor": col,
                "timestamp": timestamp_str,
                "current_value": val,
                "unit": SENSOR_THRESHOLDS[col]["unit"],
                "message": f"Warning threshold breach on {col} ({val} {SENSOR_THRESHOLDS[col]['unit']}).",
            })

    total_critical = sum(b["critical_breaches"] for b in breach_counts.values())
    total_warning = sum(b["warning_breaches"] for b in breach_counts.values())

    return {
        "processed_df": df_processed,
        "trends": trends,
        "breach_counts": breach_counts,
        "latest_events": anomaly_events,
        "total_critical_breaches": total_critical,
        "total_warning_breaches": total_warning,
    }
