"""
Health scoring and risk classification module for Pump P-101.
Calculates an explainable 0–100 Equipment Health Index and maps it
to standardized risk categories (low, medium, high, critical).
"""

from typing import Dict, Any, Tuple
import numpy as np
import pandas as pd

from analytics.config import (
    HEALTH_WEIGHTS,
    RISK_LEVEL_BANDS,
    SENSOR_THRESHOLDS,
)


def calculate_sensor_health(
    df: pd.DataFrame,
    sensor: str,
    recent_window: int = 15,
) -> Tuple[float, Dict[str, Any]]:
    """
    Computes health score (0-100) for an individual sensor based on recent telemetry.
    Takes into account recent threshold breaches, statistical anomalies, and current value.
    """
    if len(df) == 0:
        return 100.0, {"status": "no_data", "penalty": 0.0}

    recent_df = df.iloc[-min(recent_window, len(df)) :]
    latest_row = df.iloc[-1]

    penalty = 0.0
    reasons = []

    # 1. Check current value state
    is_crit_now = bool(latest_row.get(f"{sensor}_critical", False))
    is_warn_now = bool(latest_row.get(f"{sensor}_warning", False))

    if is_crit_now:
        penalty += 60.0
        reasons.append(f"Current {sensor} reading exceeds critical threshold")
    elif is_warn_now:
        penalty += 30.0
        reasons.append(f"Current {sensor} reading exceeds warning threshold")

    # 2. Check recent breach density in recent window
    if f"{sensor}_critical" in recent_df.columns:
        recent_crit_pct = float(recent_df[f"{sensor}_critical"].mean())
        if recent_crit_pct > 0 and not is_crit_now:
            penalty += recent_crit_pct * 30.0
            reasons.append(f"Recent history contains critical threshold breaches ({recent_crit_pct*100:.0f}% of window)")

    if f"{sensor}_warning" in recent_df.columns:
        recent_warn_pct = float(recent_df[f"{sensor}_warning"].mean())
        if recent_warn_pct > 0 and not is_warn_now:
            penalty += recent_warn_pct * 15.0
            reasons.append(f"Recent history contains warning threshold breaches ({recent_warn_pct*100:.0f}% of window)")

    # 3. Check statistical anomalies (Z-score outliers in recent window)
    if f"{sensor}_is_anomaly" in recent_df.columns:
        recent_anom_pct = float(recent_df[f"{sensor}_is_anomaly"].mean())
        if recent_anom_pct > 0:
            penalty += recent_anom_pct * 15.0

    # Ensure score stays within [0, 100]
    sub_score = max(0.0, min(100.0, 100.0 - penalty))

    details = {
        "sub_score": round(sub_score, 1),
        "penalty": round(penalty, 1),
        "reasons": reasons,
        "current_value": round(float(latest_row[sensor]), 2) if sensor in latest_row else None,
        "unit": SENSOR_THRESHOLDS.get(sensor, {}).get("unit", ""),
    }

    return sub_score, details


def compute_health_index(
    anomaly_result: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Computes overall equipment health score (0-100) and risk level.

    Parameters:
    -----------
    anomaly_result : dict
        Output from `run_anomaly_pipeline`.

    Returns:
    --------
    dict containing:
        - health_score (float, 0-100)
        - risk_level ('low' | 'medium' | 'high' | 'critical')
        - risk_description (str)
        - sensor_subscores (dict)
        - primary_drivers (list of str)
    """
    df = anomaly_result["processed_df"]
    trends = anomaly_result.get("trends", {})

    sensor_subscores: Dict[str, float] = {}
    sensor_details: Dict[str, Dict[str, Any]] = {}
    weighted_score = 0.0
    total_weight = 0.0

    for sensor, weight in HEALTH_WEIGHTS.items():
        if sensor in df.columns:
            sub_score, details = calculate_sensor_health(df, sensor)
            sensor_subscores[sensor] = sub_score
            sensor_details[sensor] = details
            weighted_score += sub_score * weight
            total_weight += weight

    if total_weight > 0:
        base_health = weighted_score / total_weight
    else:
        base_health = 100.0

    # Compound penalty for correlated abnormal patterns
    # (e.g. rising vibration + rising temperature + falling pressure & flow)
    compound_penalty = 0.0
    drivers = []

    vib_trend = trends.get("vibration", {}).get("direction", "stable")
    temp_trend = trends.get("temperature", {}).get("direction", "stable")
    pres_trend = trends.get("pressure", {}).get("direction", "stable")
    flow_trend = trends.get("flow_rate", {}).get("direction", "stable")

    if vib_trend == "increasing" and temp_trend == "increasing":
        compound_penalty += 10.0
        drivers.append("Concurrent upward vibration and temperature trends observed; may warrant inspection.")

    if pres_trend == "decreasing" and flow_trend == "decreasing":
        compound_penalty += 8.0
        drivers.append("Concurrent pressure and flow rate reductions observed; indicates abnormal hydraulic operating pattern.")

    final_health_score = max(0.0, min(100.0, base_health - compound_penalty))
    final_health_score = round(final_health_score, 1)

    # Classify Risk Level
    risk_level = "low"
    risk_desc = "Normal operation"

    for band in RISK_LEVEL_BANDS:
        if final_health_score >= band["min_score"]:
            risk_level = band["level"]
            risk_desc = band["description"]
            break

    # Add active breach drivers
    for sensor, details in sensor_details.items():
        for r in details.get("reasons", []):
            if r not in drivers:
                drivers.append(r)

    if not drivers:
        drivers.append("All monitored telemetry within nominal operating parameters.")

    return {
        "health_score": final_health_score,
        "risk_level": risk_level,
        "risk_description": risk_desc,
        "sensor_subscores": sensor_subscores,
        "sensor_details": sensor_details,
        "primary_drivers": drivers,
    }
