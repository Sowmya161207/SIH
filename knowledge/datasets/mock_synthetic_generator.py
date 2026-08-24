"""Synthetic Refinery Sensor Telemetry Generator for Mock Testing & Simulation.

Generates realistic time-series data for MRPL rotating equipment with:
- Gaussian measurement noise
- Configurable operational states (NORMAL, VIBRATION_SPIKE, MOTOR_OVERHEAT, LEAK, SURGE)
- Export to JSON or CSV
"""

import csv
import json
import math
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional


def generate_synthetic_telemetry(
    equipment_tag: str = "P-101A",
    unit: str = "CDU-1",
    num_samples: int = 50,
    start_time: Optional[datetime] = None,
    interval_minutes: int = 15,
    inject_anomaly_at_index: Optional[int] = 30,
    anomaly_type: str = "bearing_degradation"
) -> List[Dict[str, Any]]:
    """
    Generate synthetic sensor telemetry stream.

    :param equipment_tag: Equipment identifier (e.g. 'P-101A', 'K-101', 'P-204')
    :param unit: Refinery unit ('CDU-1', 'VGO-HT', 'FCCU')
    :param num_samples: Total number of sequential time-series samples
    :param start_time: Starting datetime (defaults to now - timedelta)
    :param interval_minutes: Sampling interval in minutes
    :param inject_anomaly_at_index: Index at which anomaly/fault starts developing
    :param anomaly_type: 'bearing_degradation', 'motor_overheat', 'seal_leak', 'compressor_surge'
    :return: List of telemetry dictionaries
    """
    if start_time is None:
        start_time = datetime(2026, 8, 24, 6, 0, 0)

    records = []
    base_vib = 1.4
    base_temp = 68.0
    base_pressure = 10.5
    base_current = 140.0

    for i in range(num_samples):
        timestamp = (start_time + timedelta(minutes=i * interval_minutes)).strftime("%Y-%m-%d %H:%M:%S")
        is_anomaly = inject_anomaly_at_index is not None and i >= inject_anomaly_at_index
        severity = min(1.0, (i - inject_anomaly_at_index) / 10.0) if is_anomaly else 0.0

        # Normal fluctuations
        vib_noise = random.gauss(0, 0.08)
        temp_noise = random.gauss(0, 0.5)
        p_noise = random.gauss(0, 0.1)

        vib = base_vib + vib_noise
        temp = base_temp + temp_noise
        press = base_pressure + p_noise
        current = base_current + random.gauss(0, 1.2)
        failure_label = None

        if is_anomaly:
            if anomaly_type == "bearing_degradation":
                vib += severity * 4.2  # Ramps up to ~5.8 mm/s
                temp += severity * 25.0 # Ramps up to ~95 deg C
                current += severity * 18.0
                failure_label = "Bearing Degradation"
            elif anomaly_type == "motor_overheat":
                temp += severity * 60.0 # Ramps up to ~130 deg C
                current += severity * 28.0
                failure_label = "Motor Overheat"
            elif anomaly_type == "seal_leak":
                press -= severity * 4.0
                failure_label = "Mechanical Seal Leak"
            elif anomaly_type == "compressor_surge":
                vib += severity * 5.0
                temp += severity * 35.0
                failure_label = "Compressor Surge"

        records.append({
            "timestamp": timestamp,
            "equipment_tag": equipment_tag,
            "unit": unit,
            "vibration_rms_mms": round(max(0.2, vib), 2),
            "bearing_temp_deg_c": round(temp, 1),
            "discharge_pressure_bar": round(press, 2),
            "motor_current_amp": round(current, 1),
            "anomaly_flag": 1 if is_anomaly else 0,
            "failure_label": failure_label
        })

    return records


def export_synthetic_dataset_to_csv(records: List[Dict[str, Any]], filepath: str) -> str:
    """Save generated records to CSV."""
    if not records:
        return filepath
    fieldnames = list(records[0].keys())
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)
    return filepath


if __name__ == "__main__":
    sample_data = generate_synthetic_telemetry(num_samples=20, inject_anomaly_at_index=12)
    print(f"Generated {len(sample_data)} sample telemetry records.")
    print("Sample record:", json.dumps(sample_data[-1], indent=2))
