"""
Health scoring and risk classification module for Pump P-101.
Calculates an explainable 0–100 Equipment Health Index and maps it
to standardized risk categories (low, medium, high, critical).
"""

from typing import Dict, Any, Tuple, List, Optional
import numpy as np
import pandas as pd

from analytics.config import (
    HEALTH_WEIGHTS,
    RISK_LEVEL_BANDS,
    SENSOR_THRESHOLDS,
    STATUS_HEALTHY,
    STATUS_WARNING,
    STATUS_CRITICAL,
)


def determine_equipment_status(
    health_score: float,
    breach_counts: Optional[Dict[str, Dict[str, int]]] = None,
    latest_events: Optional[List[Dict[str, Any]]] = None,
    risk_level: Optional[str] = None,
) -> str:
    """
    Determines overall operational status: 'healthy', 'warning', or 'critical'.

    Safety Rules:
    - CRITICAL: Any active critical breach, or health score < 50.0, or risk level 'critical'.
    - WARNING: Any active warning breach, health score between 50.0 and 79.9, or risk level 'medium'/'high'.
    - HEALTHY: Health score >= 80.0 with no active breaches and risk level 'low'.
    """
    # 1. Check for active critical threshold breach events
    if latest_events:
        for ev in latest_events:
            if ev.get("severity") == "CRITICAL":
                return STATUS_CRITICAL

    # 2. Check total critical breaches in historical/recent telemetry
    if breach_counts:
        total_crit = sum(b.get("critical_breaches", 0) for b in breach_counts.values())
        if total_crit > 0 and health_score < 60.0:
            return STATUS_CRITICAL

    # 3. Check health score threshold for critical
    if health_score < 50.0 or (risk_level and risk_level.lower() == "critical"):
        return STATUS_CRITICAL

    # 4. Check for active warning events
    if latest_events:
        for ev in latest_events:
            if ev.get("severity") == "WARNING":
                return STATUS_WARNING

    # 5. Check health score threshold for warning
    if health_score < 80.0 or (risk_level and risk_level.lower() in ["medium", "high"]):
        return STATUS_WARNING

    return STATUS_HEALTHY


def extract_explainable_issues(
    anomaly_result: Dict[str, Any],
    sensor_details: Optional[Dict[str, Any]] = None,
) -> List[str]:
    """
    Extracts a concise, human-readable list of active degradation issues,
    combining threshold breaches, trend escalations, and statistical outliers.
    """
    issues: List[str] = []
    latest_events = anomaly_result.get("latest_events", [])
    trends = anomaly_result.get("trends", {})

    # 1. Active threshold breach events
    for ev in latest_events:
        sensor = ev.get("sensor", "")
        val = ev.get("current_value")
        unit = ev.get("unit", "")
        sev = ev.get("severity", "")

        if sensor == "temperature":
            if sev == "CRITICAL":
                issues.append(f"Critical bearing overheating ({val} {unit} exceeds critical threshold)")
            else:
                issues.append(f"Elevated bearing temperature ({val} {unit} exceeds warning limit)")
        elif sensor == "vibration":
            if sev == "CRITICAL":
                issues.append(f"Critical vibration breach ({val} {unit} exceeds critical threshold)")
            else:
                issues.append(f"Elevated vibration ({val} {unit} exceeds warning limit)")
        elif sensor == "pressure":
            issues.append(f"Abnormal discharge pressure ({val} {unit} outside operating range)")
        elif sensor == "flow_rate":
            issues.append(f"Reduced pump flow rate ({val} {unit} below baseline)")
        else:
            issues.append(f"{sensor.replace('_', ' ').title()} {sev.lower()} breach ({val} {unit})")

    # 2. Significant directional trends
    vib_trend = trends.get("vibration", {})
    temp_trend = trends.get("temperature", {})
    pres_trend = trends.get("pressure", {})
    flow_trend = trends.get("flow_rate", {})

    if vib_trend.get("direction") == "increasing" and "Increasing vibration" not in " ".join(issues):
        pct = vib_trend.get("total_change_pct", 0.0)
        issues.append(f"Increasing vibration trend (+{pct}% over observation window)")

    if temp_trend.get("direction") == "increasing" and "temperature" not in " ".join(issues).lower():
        pct = temp_trend.get("total_change_pct", 0.0)
        issues.append(f"Increasing temperature trend (+{pct}% over observation window)")

    if pres_trend.get("direction") == "decreasing" and "pressure" not in " ".join(issues).lower():
        pct = pres_trend.get("total_change_pct", 0.0)
        issues.append(f"Decreasing discharge pressure trend ({pct}% over observation window)")

    if flow_trend.get("direction") == "decreasing" and "flow" not in " ".join(issues).lower():
        pct = flow_trend.get("total_change_pct", 0.0)
        issues.append(f"Decreasing flow rate trend ({pct}% throughput reduction)")

    # 3. Add sensor detail reasons if not already represented
    if sensor_details:
        for sensor, details in sensor_details.items():
            for r in details.get("reasons", []):
                if not any(sensor in iss.lower() for iss in issues):
                    issues.append(r)

    # 4. Default if no issues identified
    if not issues:
        issues.append("All sensor telemetry operating within nominal baseline parameters")

    return issues


def generate_actionable_recommendations(
    status: str,
    issues: List[str],
    trends: Optional[Dict[str, Any]] = None,
    breach_counts: Optional[Dict[str, Any]] = None,
    latest_events: Optional[List[Dict[str, Any]]] = None,
) -> List[str]:
    """
    Generates actionable maintenance and engineering recommendations
    grounded in industrial pump operating procedures and observed issues.
    """
    recs: List[str] = []
    issues_str = " ".join(issues).lower()
    trends = trends or {}

    # Critical Response
    if status == STATUS_CRITICAL or "critical" in issues_str:
        recs.append("Initiate SOP Section 9 Critical Vibration Response (notify operations, schedule physical inspection)")

    # Vibration / Coupling / Bearing
    if "vibration" in issues_str or trends.get("vibration", {}).get("direction") == "increasing":
        recs.append("Inspect coupling alignment with dial indicators and verify bearing mechanical condition")

    # Temperature / Lubrication
    if "temperature" in issues_str or "overheating" in issues_str or trends.get("temperature", {}).get("direction") == "increasing":
        recs.append("Inspect bearing lubrication level and check for lubricant degradation or contamination")

    # Pressure / Hydraulic Line
    if "pressure" in issues_str or trends.get("pressure", {}).get("direction") == "decreasing":
        recs.append("Check suction strainer differential pressure and verify discharge valve positions according to SOP Section 10")

    # Flow Rate
    if "flow" in issues_str or trends.get("flow_rate", {}).get("direction") == "decreasing":
        recs.append("Inspect pump impeller clearances and check suction line for cavitation or air entrapment")

    # History Review on degradation
    if status in [STATUS_WARNING, STATUS_CRITICAL]:
        recs.append("Review equipment maintenance history (referencing Incident INC-P101-2026-007 precedent)")

    # Nominal Fallback
    if not recs or status == STATUS_HEALTHY:
        recs = [
            "Continue routine vibration and temperature logging according to SOP Section 7",
            "Maintain scheduled preventive maintenance interval",
        ]

    # Deduplicate while preserving order
    return list(dict.fromkeys(recs))


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
    Computes overall equipment health score (0-100), status, and risk level.

    Parameters:
    -----------
    anomaly_result : dict
        Output from `run_anomaly_pipeline`.

    Returns:
    --------
    dict containing:
        - health_score (float, 0-100)
        - status ('healthy' | 'warning' | 'critical')
        - risk_level ('low' | 'medium' | 'high' | 'critical')
        - risk_description (str)
        - issues (list of str)
        - recommendations (list of str)
        - sensor_subscores (dict)
        - sensor_details (dict)
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

    # Determine Equipment Status ('healthy', 'warning', 'critical')
    status = determine_equipment_status(
        health_score=final_health_score,
        breach_counts=anomaly_result.get("breach_counts"),
        latest_events=anomaly_result.get("latest_events"),
        risk_level=risk_level,
    )

    # Add active breach drivers
    for sensor, details in sensor_details.items():
        for r in details.get("reasons", []):
            if r not in drivers:
                drivers.append(r)

    if not drivers:
        drivers.append("All monitored telemetry within nominal operating parameters.")

    # Generate explainable issues and actionable recommendations
    issues = extract_explainable_issues(anomaly_result, sensor_details)
    recommendations = generate_actionable_recommendations(
        status=status,
        issues=issues,
        trends=trends,
        breach_counts=anomaly_result.get("breach_counts", {}),
        latest_events=anomaly_result.get("latest_events", []),
    )

    return {
        "health_score": final_health_score,
        "status": status,
        "risk_level": risk_level,
        "risk_description": risk_desc,
        "issues": issues,
        "recommendations": recommendations,
        "sensor_subscores": sensor_subscores,
        "sensor_details": sensor_details,
        "primary_drivers": drivers,
    }
