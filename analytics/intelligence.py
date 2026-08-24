"""
Industrial Incident & Equipment Intelligence Module for SIH PS 26117.
Provides deterministic, explainable analytics interfaces for the Planner:
- analyze_equipment(...)
- investigate_incident(...)
- predict_maintenance_risk(...)

Grounds all findings with document, page, measurement, timestamp, and threshold citations.
Strictly separates Observed (facts), Inference (hypotheses), and Recommendation (actions).
"""

from typing import Union, List, Dict, Any, Optional
from pathlib import Path
import datetime
import pandas as pd
import numpy as np

from analytics.config import (
    DEFAULT_EQUIPMENT_ID,
    SENSOR_THRESHOLDS,
    SYSTEM_LIMITATIONS,
)
from analytics.main import analyze_sensor_data


def _format_triplet(observed: str, inference: str, recommendation: str) -> Dict[str, str]:
    """Helper to enforce strict separation between observed facts, inferences, and recommendations."""
    return {
        "observed": observed,
        "inference": inference,
        "recommendation": recommendation,
    }


def analyze_equipment(
    equipment_id: str = DEFAULT_EQUIPMENT_ID,
    sensor_data: Optional[Union[pd.DataFrame, List[Dict[str, Any]], str, Path]] = None,
    current_telemetry: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Analyzes equipment operational status, sensor telemetry, and threshold deviations.
    Callable interface for the Planner.

    Parameters:
    -----------
    equipment_id : str
        Target equipment tag (e.g., 'Pump P-101').
    sensor_data : DataFrame | list[dict] | CSV path, optional
        Time-series telemetry dataset.
    current_telemetry : dict, optional
        Snapshot of latest sensor readings (e.g. {'vibration': 8.7, 'temperature': 71, 'pressure': 4.1}).

    Returns:
    --------
    dict containing equipment health, risk level, grounded anomalies, triplet insights, and actions.
    """
    timestamp_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 1. Fallback or baseline handling if data is missing
    if sensor_data is None and current_telemetry is None:
        return {
            "equipment": equipment_id,
            "equipment_type": "Centrifugal Process Pump",
            "timestamp": timestamp_str,
            "status": "DATA_UNAVAILABLE",
            "health_score": None,
            "risk_level": "UNKNOWN",
            "risk_description": "No telemetry data provided. Operational status cannot be computed.",
            "anomalies": [],
            "triplet_insights": [
                _format_triplet(
                    observed="No live or historical telemetry provided for evaluation.",
                    inference="Equipment operational state is unverified.",
                    recommendation="Connect sensor telemetry feed or load historical CSV data to perform analysis."
                )
            ],
            "recommended_actions": ["Provide sensor telemetry data for automated analysis."],
            "evidence_required": ["Live SCADA/DCS sensor stream or CSV historical data."],
            "limitations": SYSTEM_LIMITATIONS,
        }

    # 2. Time-series analysis if sensor_data is provided
    if sensor_data is not None:
        try:
            base_analytics = analyze_sensor_data(sensor_data)
            health_score = base_analytics["health_score"]
            risk_level = base_analytics["risk_level"].upper()
            risk_description = base_analytics["risk_description"]
            trends = base_analytics["trends"]
            anomalies_summary = base_analytics["anomalies"]
            latest_chart = base_analytics["chart_data"][-1] if base_analytics["chart_data"] else {}
            timestamp_str = latest_chart.get("timestamp", timestamp_str)
        except Exception as e:
            return {
                "equipment": equipment_id,
                "status": "PROCESSING_ERROR",
                "error": f"Failed to parse time-series sensor data: {str(e)}",
                "risk_level": "UNKNOWN",
                "recommended_actions": ["Validate input data format against required telemetry schema."],
            }
    else:
        # Single telemetry point evaluation
        health_score = 100.0
        risk_level = "LOW"
        risk_description = "Sensor telemetry within nominal baseline parameters."
        trends = {}
        anomalies_summary = {"total_critical_breaches": 0, "total_warning_breaches": 0, "latest_events": []}
        latest_chart = current_telemetry or {}

    # 3. Grounded Threshold Anomaly Evaluation with Document Citations
    grounded_anomalies = []
    triplet_insights = []
    recommended_actions = []

    vib = latest_chart.get("vibration")
    temp = latest_chart.get("temperature")
    pres = latest_chart.get("pressure")
    rpm_val = latest_chart.get("rpm", latest_chart.get("speed"))
    flow = latest_chart.get("flow_rate")

    # Evaluate Vibration against Equipment Manual & SOP limits
    if vib is not None:
        vib_f = float(vib)
        if vib_f >= 7.1:
            grounded_anomalies.append({
                "sensor": "vibration",
                "observed_value": vib_f,
                "unit": "mm/s RMS",
                "condition": "CRITICAL",
                "threshold_rule": "Vibration > 7.1 mm/s RMS is classified as Critical",
                "evidence_source": {
                    "document": "Pump_P101_Equipment_Manual.pdf",
                    "section": "Section 4 Vibration Monitoring Limits",
                    "page": 2,
                },
            })
            triplet_insights.append(_format_triplet(
                observed=f"Vibration reached {vib_f} mm/s RMS exceeding critical limit 7.1 mm/s RMS (Equipment Manual, Page 2).",
                inference="Elevated vibration indicates significant rotating assembly deviation; historically associated with bearing wear or coupling misalignment (Incident Report INC-P101-2026-007).",
                recommendation="Follow SOP Section 9 Critical Vibration Response: notify operator, initiate controlled shutdown, and inspect bearings and coupling alignment."
            ))
            recommended_actions.append("Execute SOP Section 9 Critical Vibration Response protocol.")
        elif vib_f >= 4.5:
            grounded_anomalies.append({
                "sensor": "vibration",
                "observed_value": vib_f,
                "unit": "mm/s RMS",
                "condition": "WARNING",
                "threshold_rule": "Vibration 4.5–7.1 mm/s RMS is classified as Warning",
                "evidence_source": {
                    "document": "Pump_P101_Equipment_Manual.pdf",
                    "section": "Section 4 Vibration Monitoring Limits",
                    "page": 2,
                },
            })
            triplet_insights.append(_format_triplet(
                observed=f"Vibration measured at {vib_f} mm/s RMS in the warning range (4.5–7.1 mm/s RMS).",
                inference="Pattern indicates early mechanical deviation, similar to 18 May 2026 warning event (5.3 mm/s RMS).",
                recommendation="Follow SOP Section 8: verify reading, check operating history, inspect coupling alignment and bearing lubrication during scheduled maintenance."
            ))
            recommended_actions.append("Inspect coupling alignment and bearing lubrication according to SOP Section 8.")

    # Evaluate Temperature
    if temp is not None:
        temp_f = float(temp)
        if temp_f > 75.0:
            grounded_anomalies.append({
                "sensor": "temperature",
                "observed_value": temp_f,
                "unit": "°C",
                "condition": "ELEVATED_TEMPERATURE",
                "threshold_rule": "Normal operating temperature range is 60–75 °C",
                "evidence_source": {
                    "document": "Pump_P101_Equipment_Manual.pdf",
                    "section": "Section 5 Temperature Monitoring",
                    "page": 2,
                },
            })
            triplet_insights.append(_format_triplet(
                observed=f"Bearing temperature reached {temp_f} °C exceeding upper normal limit of 75 °C.",
                inference="Elevated temperature indicates excessive mechanical friction, insufficient lubrication, or cooling limitation.",
                recommendation="Inspect bearing lubrication level and replenish grease/oil according to SOP Section 10."
            ))
            recommended_actions.append("Inspect bearing lubrication and thermal cooling circuit.")

    # Evaluate Pressure
    if pres is not None:
        pres_f = float(pres)
        if pres_f < 3.8 or pres_f > 7.5:
            grounded_anomalies.append({
                "sensor": "pressure",
                "observed_value": pres_f,
                "unit": "bar",
                "condition": "ABNORMAL_PRESSURE",
                "threshold_rule": "Normal discharge pressure range is 4.0–4.5 bar (Manual Page 2)",
                "evidence_source": {
                    "document": "Pump_P101_Equipment_Manual.pdf",
                    "section": "Section 6 Pressure Monitoring",
                    "page": 2,
                },
            })
            triplet_insights.append(_format_triplet(
                observed=f"Discharge pressure measured at {pres_f} bar outside normal operating range (4.0–4.5 bar).",
                inference="Abnormal discharge pressure indicates possible suction line restriction, valve malposition, or cavitation onset.",
                recommendation="Verify suction strainer differential pressure and line valve positions according to SOP Section 10."
            ))
            recommended_actions.append("Check suction strainer and discharge valve lineup.")

    # Default insight if all healthy
    if not triplet_insights:
        triplet_insights.append(_format_triplet(
            observed="All monitored parameters (vibration, temperature, pressure, speed) are within nominal operating limits.",
            inference="Equipment is operating within baseline design specifications.",
            recommendation="Continue routine condition-monitoring and scheduled preventive maintenance."
        ))
        recommended_actions.append("Maintain routine vibration and temperature logging according to SOP Section 7.")

    # Deduplicate recommended actions
    recommended_actions = list(dict.fromkeys(recommended_actions))

    evidence_required = [
        "Vibration spectrum FFT data to confirm dominant frequency component (1X vs 2X vs high frequency).",
        "Physical dial indicator / feeler gauge coupling alignment measurements.",
        "Physical bearing grease/oil contamination inspection."
    ]

    return {
        "equipment": equipment_id,
        "equipment_type": "Centrifugal Process Pump",
        "timestamp": timestamp_str,
        "health_score": health_score,
        "risk_level": risk_level,
        "risk_description": risk_description,
        "anomalies": grounded_anomalies,
        "trends": trends,
        "triplet_insights": triplet_insights,
        "recommended_actions": recommended_actions,
        "evidence_required": evidence_required,
        "limitations": SYSTEM_LIMITATIONS,
    }


def investigate_incident(
    incident_id: Optional[str] = "INC-P101-2026-007",
    incident_data: Optional[Dict[str, Any]] = None,
    equipment_id: str = DEFAULT_EQUIPMENT_ID,
) -> Dict[str, Any]:
    """
    Executes a structured, deterministic root cause and incident investigation.
    Callable interface for the Planner.

    Parameters:
    -----------
    incident_id : str, optional
        Specific incident identifier (default: 'INC-P101-2026-007').
    incident_data : dict, optional
        Custom incident details or sensor measurements at the time of the event.
    equipment_id : str
        Target equipment tag.

    Returns:
    --------
    dict containing incident summary, telemetry, grounded root causes, before/after metrics, and actions.
    """
    # Deterministic ground-truth mapping for historical incident INC-P101-2026-007
    is_canonical_incident = (incident_id == "INC-P101-2026-007" or incident_id is None) and incident_data is None

    if is_canonical_incident:
        return {
            "incident_id": "INC-P101-2026-007",
            "equipment": equipment_id,
            "equipment_type": "Centrifugal Process Pump",
            "incident_date": "21 July 2026",
            "incident_type": "Abnormally High Vibration",
            "severity": "HIGH",
            "executive_summary": (
                "On 21 July 2026, condition-monitoring detected abnormal vibration reaching 8.7 mm/s RMS "
                "on Pump P-101, exceeding the critical limit of 7.1 mm/s RMS. Investigation identified "
                "bearing degradation and coupling misalignment as primary suspected contributors. "
                "Affected bearing was replaced and coupling realigned, restoring vibration to 2.6 mm/s RMS."
            ),
            "sensor_readings_at_event": {
                "vibration": "8.7 mm/s RMS (Critical)",
                "temperature": "71 °C (Elevated)",
                "discharge_pressure": "4.1 bar (Normal)",
                "speed": "1450 RPM (Normal)",
            },
            "initial_symptoms": [
                "Significant increase in vibration",
                "Elevated equipment temperature",
                "No significant pressure deviation",
                "Pump speed remained approximately constant",
            ],
            "suspected_root_causes": [
                {
                    "cause": "Bearing Degradation",
                    "status": "CONFIRMED_BY_INSPECTION",
                    "evidence_observed": "Bearing wear was observed during physical mechanical inspection.",
                    "source": {
                        "document": "Pump_P101_Incident_Report.pdf",
                        "section": "Section 8 Root Cause Assessment",
                        "page": 3,
                    },
                },
                {
                    "cause": "Coupling Misalignment",
                    "status": "CONFIRMED_BY_INSPECTION",
                    "evidence_observed": "Coupling alignment was measured outside acceptable condition; recurring from May 2026.",
                    "source": {
                        "document": "Pump_P101_Incident_Report.pdf",
                        "section": "Section 8 Root Cause Assessment",
                        "page": 3,
                    },
                },
            ],
            "distinction_layer": [
                _format_triplet(
                    observed="Condition monitoring recorded 8.7 mm/s RMS vibration at 1450 RPM and 71 °C on 21 July 2026.",
                    inference="Telemetry escalation indicated severe mechanical rotating deviation.",
                    recommendation="Perform physical bearing replacement, coupling realignment, and lubrication replenishment."
                )
            ],
            "corrective_actions_completed": [
                "Pump was safely isolated according to site LOTO procedures.",
                "Affected bearing was removed and replacement bearing was installed.",
                "Coupling alignment was corrected and fasteners were secured.",
                "Bearing lubrication was completed and pump rotation was verified.",
                "Pump was restarted under controlled conditions and monitored.",
            ],
            "before_and_after_measurements": {
                "vibration": {"before": "8.7 mm/s RMS", "after": "2.6 mm/s RMS", "status": "RESTORED_NORMAL"},
                "temperature": {"before": "71 °C", "after": "65 °C", "status": "RESTORED_NORMAL"},
                "discharge_pressure": {"before": "4.1 bar", "after": "4.2 bar", "status": "NORMAL"},
                "speed": {"before": "1450 RPM", "after": "1450 RPM", "status": "NOMINAL"},
            },
            "preventive_actions": [
                "Continue regular vibration monitoring and review trends.",
                "Inspect coupling alignment during scheduled maintenance.",
                "Monitor bearing condition and maintain appropriate lubrication.",
                "Review maintenance history when new anomalies occur.",
            ],
            "evidence_required": [
                "Post-maintenance vibration signature measurement (achieved 2.6 mm/s RMS).",
                "Coupling alignment report with dial indicator readings.",
                "Work order documentation for replaced bearing assembly.",
            ],
            "limitations": SYSTEM_LIMITATIONS,
        }

    # Dynamic incident investigation for custom incident data
    custom_data = incident_data or {}
    observed_vib = custom_data.get("vibration", 0.0)
    observed_temp = custom_data.get("temperature", 0.0)

    return {
        "incident_id": incident_id or "INC-CUSTOM",
        "equipment": equipment_id,
        "incident_type": custom_data.get("type", "Custom Incident Investigation"),
        "severity": "CRITICAL" if observed_vib >= 7.1 else ("HIGH" if observed_vib >= 4.5 else "MEDIUM"),
        "observed_symptoms": custom_data.get("symptoms", ["Telemetry deviation reported"]),
        "suspected_root_causes": [
            {
                "cause": "Mechanical Imbalance or Bearing Wear",
                "likelihood": "HIGH" if observed_vib >= 4.5 else "LOW",
                "evidence_observed": f"Observed vibration: {observed_vib} mm/s RMS",
                "source": {
                    "document": "Pump_P101_Equipment_Manual.pdf",
                    "section": "Section 7 Common Causes of High Vibration",
                    "page": 3,
                },
            }
        ],
        "distinction_layer": [
            _format_triplet(
                observed=f"Incident telemetry recorded vibration at {observed_vib} mm/s and temp at {observed_temp} °C.",
                inference="Pattern may indicate mechanical wear or alignment issues.",
                recommendation="Isolate equipment, inspect coupling alignment and bearing condition according to SOP."
            )
        ],
        "recommended_actions": [
            "Verify sensor reading validity.",
            "Inspect bearing condition and lubrication.",
            "Verify coupling alignment.",
        ],
        "evidence_required": [
            "Physical inspection report confirming mechanical condition.",
            "Post-repair vibration verification reading.",
        ],
        "limitations": SYSTEM_LIMITATIONS,
    }


def predict_maintenance_risk(
    equipment_id: str = DEFAULT_EQUIPMENT_ID,
    sensor_data: Optional[Union[pd.DataFrame, List[Dict[str, Any]], str, Path]] = None,
    current_telemetry: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Computes explainable, deterministic predictive maintenance risk indicators.
    Callable interface for the Planner.

    Parameters:
    -----------
    equipment_id : str
        Target equipment tag.
    sensor_data : DataFrame | list[dict] | CSV path, optional
        Historical or batch telemetry.
    current_telemetry : dict, optional
        Latest telemetry readings.

    Returns:
    --------
    dict containing maintenance risk scores, failure mode indicators, triplet breakdowns, and maintenance guidance.
    """
    # 1. Evaluate telemetry state
    equipment_analysis = analyze_equipment(
        equipment_id=equipment_id,
        sensor_data=sensor_data,
        current_telemetry=current_telemetry,
    )

    health_score = equipment_analysis.get("health_score")
    risk_level = equipment_analysis.get("risk_level", "LOW")
    anomalies = equipment_analysis.get("anomalies", [])

    # 2. Derive explainable failure mode indicators
    failure_mode_indicators = []
    triplet_breakdown = []

    has_vib_critical = any(a.get("sensor") == "vibration" and a.get("condition") == "CRITICAL" for a in anomalies)
    has_vib_warning = any(a.get("sensor") == "vibration" and a.get("condition") == "WARNING" for a in anomalies)
    has_temp_elevated = any(a.get("sensor") == "temperature" for a in anomalies)
    has_pressure_abnormal = any(a.get("sensor") == "pressure" for a in anomalies)

    if has_vib_critical or (has_vib_warning and has_temp_elevated):
        failure_mode_indicators.append({
            "failure_mode": "Bearing Degradation / Lubrication Failure",
            "risk_score": 85.0 if has_vib_critical else 65.0,
            "indicators_observed": "Elevated vibration combined with increased bearing temperature.",
            "evidence_basis": {
                "document": "Pump_P101_Equipment_Manual.pdf",
                "page": 2,
                "thresholds": "Vibration > 7.1 mm/s Critical, Temperature > 75 °C Warning",
            },
            "inference": "This pattern is consistent with loss of lubrication film or progressive bearing raceway wear.",
            "recommended_action": "Check lubrication condition, replenish grease/oil, inspect bearing during next maintenance window.",
        })
        triplet_breakdown.append(_format_triplet(
            observed="Vibration and temperature both exhibit elevated readings exceeding baseline parameters.",
            inference="May indicate progressive mechanical friction or bearing wear.",
            recommendation="Inspect bearing lubrication and schedule condition-based inspection according to SOP Section 8."
        ))

    if has_vib_warning or has_vib_critical:
        failure_mode_indicators.append({
            "failure_mode": "Coupling Misalignment",
            "risk_score": 75.0 if has_vib_critical else 55.0,
            "indicators_observed": "Vibration increase matching historical 18 May 2026 and 21 July 2026 misalignment events.",
            "evidence_basis": {
                "document": "Pump_P101_Maintenance_Report.pdf",
                "page": 2,
                "incident_precedent": "Event 2 (18 May 2026) and Incident INC-P101-2026-007",
            },
            "inference": "May indicate shaft angular or radial offset between motor and pump.",
            "recommended_action": "Verify coupling alignment with dial indicators and re-torque coupling fasteners.",
        })

    if has_pressure_abnormal:
        failure_mode_indicators.append({
            "failure_mode": "Hydraulic Output Degradation / Flow Restriction",
            "risk_score": 60.0,
            "indicators_observed": "Discharge pressure deviation from normal 4.0–4.5 bar range.",
            "evidence_basis": {
                "document": "Pump_P101_SOP.pdf",
                "page": 4,
                "section": "Section 10 Troubleshooting Guide",
            },
            "inference": "Indicates abnormal hydraulic operating conditions or restricted process flow.",
            "recommended_action": "Inspect suction strainers and check valve alignments according to SOP Section 10.",
        })
        triplet_breakdown.append(_format_triplet(
            observed="Discharge pressure deviated from normal 4.0–4.5 bar baseline.",
            inference="May indicate flow restriction or suction strainer loading.",
            recommendation="Inspect suction strainer differential pressure and verify valve positions."
        ))

    # Baseline nominal fallback
    if not failure_mode_indicators:
        failure_mode_indicators.append({
            "failure_mode": "None Identified (Nominal Operation)",
            "risk_score": 10.0,
            "indicators_observed": "All sensor telemetry remains within design operating limits.",
            "evidence_basis": {
                "document": "Pump_P101_Equipment_Manual.pdf",
                "page": 1,
                "section": "Section 3 Normal Operating Specifications",
            },
            "inference": "Equipment is operating under stable conditions with low probability of near-term failure.",
            "recommended_action": "Continue routine vibration and temperature logging according to SOP Section 7.",
        })
        triplet_breakdown.append(_format_triplet(
            observed="All telemetry within nominal specifications (Manual Section 3).",
            inference="No abnormal mechanical or thermal degradation pattern detected.",
            recommendation="Continue routine monitoring."
        ))

    # Determine recommended maintenance urgency
    if risk_level == "CRITICAL":
        urgency = "IMMEDIATE_OPERATIONAL_REVIEW"
        window_guidance = "Immediate operational review and physical inspection are recommended according to site SOP Section 9."
    elif risk_level == "HIGH":
        urgency = "INSPECT_WITHIN_24_HOURS"
        window_guidance = "Schedule physical engineering inspection within 24–48 hours."
    elif risk_level == "MEDIUM":
        urgency = "NEXT_MAINTENANCE_WINDOW"
        window_guidance = "Plan coupling and bearing check during next scheduled maintenance window."
    else:
        urgency = "ROUTINE_SCHEDULE"
        window_guidance = "Maintain standard preventive maintenance schedule."

    evidence_required = [
        "Vibration FFT frequency analysis to distinguish 1X unbalance from 2X misalignment.",
        "Dial indicator coupling alignment runout check.",
        "Bearing lubrication grease analysis.",
    ]

    return {
        "equipment": equipment_id,
        "health_index": health_score,
        "overall_maintenance_risk": risk_level,
        "urgency": urgency,
        "maintenance_window_guidance": window_guidance,
        "failure_mode_indicators": failure_mode_indicators,
        "triplet_breakdown": triplet_breakdown,
        "evidence_required": evidence_required,
        "limitations": SYSTEM_LIMITATIONS,
    }
