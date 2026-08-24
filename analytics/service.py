"""
Equipment Health Analytics Service for SIH 26117.
Provides clean, explainable, backend-ready Python APIs for industrial equipment health,
status classification, threshold violation tracking, trend analysis, and actionable recommendations.
"""

from typing import Union, List, Dict, Any, Optional
from pathlib import Path
import pandas as pd
import numpy as np

from analytics.config import (
    DEFAULT_EQUIPMENT_ID,
    SENSOR_COLUMNS,
    SENSOR_THRESHOLDS,
    HEALTH_WEIGHTS,
    RISK_LEVEL_BANDS,
    DEFAULT_MA_WINDOW,
    Z_SCORE_THRESHOLD,
    SYSTEM_LIMITATIONS,
    STATUS_HEALTHY,
    STATUS_WARNING,
    STATUS_CRITICAL,
)
from analytics.main import analyze_sensor_data, _to_json_serializable
from analytics.scoring.health_score import (
    determine_equipment_status,
    extract_explainable_issues,
    generate_actionable_recommendations,
)


class EquipmentHealthService:
    """
    Service layer providing clean, explainable, backend-ready equipment health evaluation.
    Supports time-series datasets (CSV, DataFrame, list of dicts) and single telemetry snapshots.
    """

    @classmethod
    def get_health_summary(
        cls,
        data: Union[pd.DataFrame, List[Dict[str, Any]], Dict[str, Any], str, Path],
        equipment_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Computes a concise, backend-ready equipment health summary.

        Expected output schema:
        -----------------------
        {
            "equipment_id": "P-101",
            "health_score": 72.0,
            "status": "warning",
            "risk_level": "medium",
            "issues": [
                "Elevated bearing temperature (78.5 °C exceeds 75.0 °C warning limit)",
                "Increasing vibration trend (+18.2% over observation window)"
            ],
            "metrics": {
                "vibration": 4.8,
                "temperature": 78.5,
                "pressure": 5.9,
                "rpm": 2948.0,
                "flow_rate": 112.0
            },
            "recommendations": [
                "Inspect bearing lubrication level and check for lubricant degradation",
                "Inspect coupling alignment during scheduled maintenance window"
            ]
        }
        """
        # 1. Handle single telemetry snapshot (dict with sensor keys and numeric values)
        if isinstance(data, dict) and not any(isinstance(v, list) for v in data.values()):
            return cls._evaluate_snapshot_summary(data, equipment_id=equipment_id)

        # 2. Time-series batch evaluation
        full_res = analyze_sensor_data(data)
        eq_id = equipment_id or full_res.get("equipment_id") or full_res.get("equipment", DEFAULT_EQUIPMENT_ID)

        summary_output = {
            "equipment_id": eq_id,
            "health_score": full_res["health_score"],
            "status": full_res["status"],
            "risk_level": full_res["risk_level"],
            "issues": full_res["issues"],
            "metrics": full_res["metrics"],
            "recommendations": full_res["recommendations"],
        }
        return _to_json_serializable(summary_output)

    @classmethod
    def get_full_assessment(
        cls,
        data: Union[pd.DataFrame, List[Dict[str, Any]], Dict[str, Any], str, Path],
        equipment_id: Optional[str] = None,
        ma_window: int = DEFAULT_MA_WINDOW,
        z_threshold: float = Z_SCORE_THRESHOLD,
    ) -> Dict[str, Any]:
        """
        Provides comprehensive equipment health intelligence including:
        - Health score, status ('healthy' | 'warning' | 'critical'), risk level
        - Explainable issues and actionable maintenance recommendations
        - Monitored metrics snapshot
        - Threshold violations breakdown (critical and warning counts)
        - Trend analysis (direction, slope, percentage change, interpretation)
        - Statistical anomalies and Z-score outlier summaries
        - Failure mode indicators (bearing degradation, misalignment, cavitation)
        - Chart-ready time-series records
        """
        # Handle snapshot dict
        if isinstance(data, dict) and not any(isinstance(v, list) for v in data.values()):
            summary = cls._evaluate_snapshot_summary(data, equipment_id=equipment_id)
            failure_modes = cls._derive_failure_modes(summary["issues"], summary["metrics"], {})
            full_out = {
                **summary,
                "threshold_violations": {
                    "critical_breaches": 1 if summary["status"] == STATUS_CRITICAL else 0,
                    "warning_breaches": 1 if summary["status"] == STATUS_WARNING else 0,
                    "events": summary["issues"],
                },
                "trends": {},
                "anomaly_summary": {
                    "summary": "Snapshot evaluation (single measurement point)",
                    "statistical_outliers": 0,
                },
                "failure_modes": failure_modes,
                "limitations": SYSTEM_LIMITATIONS,
            }
            return _to_json_serializable(full_out)

        # Full time-series analysis
        full_res = analyze_sensor_data(data, ma_window=ma_window, z_threshold=z_threshold)
        eq_id = equipment_id or full_res.get("equipment_id") or full_res.get("equipment", DEFAULT_EQUIPMENT_ID)

        # Derive failure modes
        failure_modes = cls._derive_failure_modes(
            full_res["issues"],
            full_res["metrics"],
            full_res.get("trends", {}),
        )

        full_assessment = {
            "equipment_id": eq_id,
            "health_score": full_res["health_score"],
            "status": full_res["status"],
            "risk_level": full_res["risk_level"],
            "risk_description": full_res["risk_description"],
            "issues": full_res["issues"],
            "metrics": full_res["metrics"],
            "recommendations": full_res["recommendations"],
            "threshold_violations": {
                "total_critical_breaches": full_res["anomalies"]["total_critical_breaches"],
                "total_warning_breaches": full_res["anomalies"]["total_warning_breaches"],
                "by_sensor": full_res["anomalies"]["by_sensor"],
                "latest_events": full_res["anomalies"]["latest_events"],
            },
            "trends": full_res["trends"],
            "anomaly_summary": full_res["anomalies"],
            "failure_modes": failure_modes,
            "health_breakdown": full_res["health_breakdown"],
            "chart_data": full_res["chart_data"],
            "limitations": SYSTEM_LIMITATIONS,
        }
        return _to_json_serializable(full_assessment)

    @classmethod
    def evaluate_snapshot(
        cls,
        current_telemetry: Dict[str, Any],
        equipment_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Evaluates a real-time single measurement snapshot (e.g. from IoT gateway or DCS).
        """
        return cls._evaluate_snapshot_summary(current_telemetry, equipment_id=equipment_id)

    @classmethod
    def _evaluate_snapshot_summary(
        cls,
        telemetry: Dict[str, Any],
        equipment_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Internal evaluator for single-point telemetry snapshots.
        """
        eq_id = equipment_id or telemetry.get("pump_id", telemetry.get("equipment_id", DEFAULT_EQUIPMENT_ID))
        
        # Extract metrics
        metrics: Dict[str, float] = {}
        for col in SENSOR_COLUMNS:
            val = telemetry.get(col)
            if val is not None:
                try:
                    metrics[col] = round(float(val), 2)
                except (ValueError, TypeError):
                    pass

        # If rpm was passed as 'speed', support it
        if "rpm" not in metrics and "speed" in telemetry:
            try:
                metrics["rpm"] = round(float(telemetry["speed"]), 1)
            except (ValueError, TypeError):
                pass

        # Calculate penalties, breaches, and issues
        total_weight = 0.0
        weighted_score = 0.0
        issues: List[str] = []
        has_critical = False
        has_warning = False

        for sensor, weight in HEALTH_WEIGHTS.items():
            total_weight += weight
            if sensor not in metrics:
                weighted_score += 100.0 * weight
                continue

            val = metrics[sensor]
            limits = SENSOR_THRESHOLDS.get(sensor, {})
            t_type = limits.get("type", "upper_bound")
            unit = limits.get("unit", "")
            sensor_penalty = 0.0

            if t_type == "upper_bound":
                crit_max = limits.get("critical_max", float("inf"))
                warn_max = limits.get("warning_max", float("inf"))

                if val >= crit_max:
                    sensor_penalty = 60.0
                    has_critical = True
                    issues.append(f"Critical {sensor} breach ({val} {unit} exceeds {crit_max} {unit} critical limit)")
                elif val >= warn_max:
                    sensor_penalty = 30.0
                    has_warning = True
                    issues.append(f"Elevated {sensor} ({val} {unit} exceeds {warn_max} {unit} warning limit)")

            elif t_type == "range":
                crit_min = limits.get("critical_min", float("-inf"))
                crit_max = limits.get("critical_max", float("inf"))
                warn_min = limits.get("warning_min", float("-inf"))
                warn_max = limits.get("warning_max", float("inf"))

                if val <= crit_min or val >= crit_max:
                    sensor_penalty = 55.0
                    has_critical = True
                    issues.append(f"Critical {sensor} breach ({val} {unit} outside critical band [{crit_min}-{crit_max}])")
                elif val <= warn_min or val >= warn_max:
                    sensor_penalty = 25.0
                    has_warning = True
                    issues.append(f"Abnormal {sensor} ({val} {unit} outside normal range [{warn_min}-{warn_max}])")

            sub_score = max(0.0, 100.0 - sensor_penalty)
            weighted_score += sub_score * weight

        health_score = round(weighted_score / total_weight, 1) if total_weight > 0 else 100.0

        # Classify risk level
        risk_level = "low"
        for band in RISK_LEVEL_BANDS:
            if health_score >= band["min_score"]:
                risk_level = band["level"]
                break

        # Determine status
        if has_critical or health_score < 50.0 or risk_level == "critical":
            status = STATUS_CRITICAL
        elif has_warning or health_score < 80.0 or risk_level in ["medium", "high"]:
            status = STATUS_WARNING
        else:
            status = STATUS_HEALTHY

        if not issues:
            issues.append("All sensor telemetry operating within nominal baseline parameters")

        recommendations = generate_actionable_recommendations(
            status=status,
            issues=issues,
            trends={},
            breach_counts={},
            latest_events=[],
        )

        return _to_json_serializable({
            "equipment_id": str(eq_id),
            "health_score": health_score,
            "status": status,
            "risk_level": risk_level,
            "issues": issues,
            "metrics": metrics,
            "recommendations": recommendations,
        })

    @classmethod
    def _derive_failure_modes(
        cls,
        issues: List[str],
        metrics: Dict[str, float],
        trends: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """
        Derives explainable industrial pump failure modes based on observed metrics and trends.
        """
        modes: List[Dict[str, Any]] = []
        issues_str = " ".join(issues).lower()

        vib_val = metrics.get("vibration", 0.0)
        temp_val = metrics.get("temperature", 0.0)
        pres_val = metrics.get("pressure", 6.0)

        # 1. Bearing Degradation
        if "bearing" in issues_str or "overheating" in issues_str or (vib_val >= 4.5 and temp_val >= 75.0):
            modes.append({
                "failure_mode": "Bearing Degradation / Lubrication Failure",
                "likelihood": "HIGH" if (vib_val >= 7.0 or temp_val >= 85.0) else "MEDIUM",
                "risk_score": 85.0 if vib_val >= 7.0 else 65.0,
                "evidence": f"Vibration={vib_val} mm/s, Temperature={temp_val} °C",
                "action": "Inspect bearing lubrication and schedule physical bearing replacement if wear is confirmed.",
            })

        # 2. Coupling Misalignment
        if "vibration" in issues_str or vib_val >= 4.5 or trends.get("vibration", {}).get("direction") == "increasing":
            modes.append({
                "failure_mode": "Coupling Misalignment / Mechanical Imbalance",
                "likelihood": "HIGH" if vib_val >= 7.0 else "MEDIUM",
                "risk_score": 75.0 if vib_val >= 7.0 else 55.0,
                "evidence": f"Elevated vibration={vib_val} mm/s RMS (historical precedent: Incident INC-P101-2026-007)",
                "action": "Verify radial and axial coupling alignment using dial indicators.",
            })

        # 3. Hydraulic Restriction / Cavitation
        if "pressure" in issues_str or pres_val < 4.8 or trends.get("pressure", {}).get("direction") == "decreasing":
            modes.append({
                "failure_mode": "Hydraulic Output Degradation / Flow Restriction",
                "likelihood": "HIGH" if pres_val < 3.8 else "MEDIUM",
                "risk_score": 60.0,
                "evidence": f"Discharge pressure={pres_val} bar below normal baseline band",
                "action": "Inspect suction strainers, check valve lineup, and verify NPSH margin to prevent cavitation.",
            })

        # Nominal Fallback
        if not modes:
            modes.append({
                "failure_mode": "None Identified (Nominal Operation)",
                "likelihood": "LOW",
                "risk_score": 10.0,
                "evidence": "All monitored sensor telemetry within nominal design specifications.",
                "action": "Continue routine vibration and temperature condition monitoring.",
            })

        return modes


# =====================================================================
# Functional Convenience APIs
# =====================================================================

def get_equipment_health(
    data: Union[pd.DataFrame, List[Dict[str, Any]], Dict[str, Any], str, Path],
    equipment_id: Optional[str] = None,
    mode: str = "summary",
) -> Dict[str, Any]:
    """
    Primary convenience function for Backend Engineers.

    Parameters:
    -----------
    data : pd.DataFrame | list[dict] | dict | str | Path
        Sensor telemetry time series or real-time snapshot.
    equipment_id : str, optional
        Equipment tag (e.g. 'P-101' or 'Pump P-101').
    mode : 'summary' | 'full' | 'detailed', default='summary'
        'summary': Clean concise payload (equipment_id, health_score, status, risk_level, issues, metrics, recommendations).
        'full' / 'detailed': Complete intelligence payload with trends, threshold violations, failure modes, and chart series.

    Returns:
    --------
    dict (100% JSON serializable)
    """
    if mode.lower() in ["full", "detailed"]:
        return EquipmentHealthService.get_full_assessment(data, equipment_id=equipment_id)
    return EquipmentHealthService.get_health_summary(data, equipment_id=equipment_id)
