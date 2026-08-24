"""MetroPT Industrial Compressor Sensor Telemetry Dataset Loader & Anomaly Processor.

Curated for MRPL Rotating Machinery & Wet Gas Compressor (K-101 / API 617).
Features:
- Vibration (mm/s RMS)
- Motor Temperature (deg C)
- Compressor Temperature (deg C)
- Output Pressure TP2 / TP3 (bar)
- Motor Current (Amps)
- Operational States & Anomaly Labels
"""

import csv
import json
import os
from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Optional


@dataclass
class TelemetryRecord:
    timestamp: str
    equipment_tag: str
    tp2_pressure_bar: float        # Compressor output pressure
    tp3_pressure_bar: float        # Filtered output pressure
    t_motor_deg_c: float           # Motor temperature
    t_compressor_deg_c: float      # Compressor head temperature
    t_ambient_deg_c: float         # Ambient temperature
    vibration_rms_mms: float       # Vibration velocity RMS
    motor_current_amp: float       # Electric current
    oil_level_status: str          # Normal, Low, Critical
    anomaly_flag: int              # 0: Normal, 1: Anomaly
    failure_label: Optional[str]   # e.g., "Bearing Degradation", "Air Leak", "Motor Overheat", None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class MetroPTDatasetLoader:
    """Loader and feature extractor for MetroPT Compressor Sensor Telemetry."""

    def __init__(self, data_path: Optional[str] = None):
        if not data_path:
            data_path = os.path.join(os.path.dirname(__file__), "metropt_compressor_telemetry.csv")
        self.data_path = data_path
        self.records: List[TelemetryRecord] = []
        if os.path.exists(self.data_path):
            self.load_data()

    def load_data(self) -> int:
        """Load telemetry records from CSV."""
        self.records = []
        with open(self.data_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                rec = TelemetryRecord(
                    timestamp=row["timestamp"],
                    equipment_tag=row["equipment_tag"],
                    tp2_pressure_bar=float(row["tp2_pressure_bar"]),
                    tp3_pressure_bar=float(row["tp3_pressure_bar"]),
                    t_motor_deg_c=float(row["t_motor_deg_c"]),
                    t_compressor_deg_c=float(row["t_compressor_deg_c"]),
                    t_ambient_deg_c=float(row["t_ambient_deg_c"]),
                    vibration_rms_mms=float(row["vibration_rms_mms"]),
                    motor_current_amp=float(row["motor_current_amp"]),
                    oil_level_status=row["oil_level_status"],
                    anomaly_flag=int(row["anomaly_flag"]),
                    failure_label=row["failure_label"] if row["failure_label"] else None
                )
                self.records.append(rec)
        return len(self.records)

    def get_summary_statistics(self) -> Dict[str, Any]:
        """Compute summary statistics for telemetry channels."""
        if not self.records:
            return {}

        vibs = [r.vibration_rms_mms for r in self.records]
        t_motors = [r.t_motor_deg_c for r in self.records]
        tp2s = [r.tp2_pressure_bar for r in self.records]
        currents = [r.motor_current_amp for r in self.records]
        anomalies = [r for r in self.records if r.anomaly_flag == 1]

        return {
            "total_samples": len(self.records),
            "anomaly_samples": len(anomalies),
            "vibration_rms_max": round(max(vibs), 2),
            "vibration_rms_mean": round(sum(vibs) / len(vibs), 2),
            "motor_temp_max_deg_c": round(max(t_motors), 2),
            "motor_temp_mean_deg_c": round(sum(t_motors) / len(t_motors), 2),
            "tp2_pressure_mean_bar": round(sum(tp2s) / len(tp2s), 2),
            "motor_current_mean_amp": round(sum(currents) / len(currents), 2),
            "detected_failure_modes": list(dict.fromkeys(r.failure_label for r in anomalies if r.failure_label))
        }

    def generate_sensor_evidence_findings(self) -> List[Dict[str, Any]]:
        """
        Extract actionable sensor evidence lines from anomalous telemetry intervals.
        Feeds directly into the Claim Verification Layer.
        """
        findings = []
        for r in self.records:
            if r.anomaly_flag == 1:
                evidence_items = []
                if r.vibration_rms_mms > 4.5:
                    evidence_items.append(f"Vibration telemetry reading {r.vibration_rms_mms:.2f} mm/s RMS on {r.equipment_tag} (Threshold 4.5 mm/s)")
                if r.t_motor_deg_c >= 110.0:
                    evidence_items.append(f"Motor temperature reached {r.t_motor_deg_c:.1f} deg C on {r.equipment_tag} (High Alarm threshold 110.0 deg C)")
                if r.oil_level_status != "Normal":
                    evidence_items.append(f"Lube oil reservoir level indicated {r.oil_level_status} status on {r.equipment_tag}")
                if r.tp2_pressure_bar < 7.0:
                    evidence_items.append(f"Discharge pressure TP2 dropped to {r.tp2_pressure_bar:.2f} bar on {r.equipment_tag}")

                findings.append({
                    "timestamp": r.timestamp,
                    "equipment_tag": r.equipment_tag,
                    "hypothesis": f"Possible {r.failure_label.lower()} on {r.equipment_tag}." if r.failure_label else f"Operational anomaly on {r.equipment_tag}.",
                    "sensor_evidence": evidence_items
                })
        return findings
