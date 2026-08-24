"""
Synthetic Demo Sensor Data Generator for Pump P-101.
SIH26117 - Predictive Maintenance & Industrial Telemetry Analytics.

DISCLAIMER:
-----------
This dataset contains purely synthetic, simulated sensor telemetry generated
for demonstration, development, and hackathon evaluation purposes.
It is NOT real MRPL operational data.
"""

from pathlib import Path
from typing import Optional
import numpy as np
import pandas as pd


def generate_pump_p101_data(
    n_records: int = 250,
    output_path: Optional[str] = None,
    seed: int = 42,
) -> pd.DataFrame:
    """
    Generates synthetic industrial sensor telemetry for Pump P-101.

    Parameters:
    -----------
    n_records : int, default=250
        Total number of 5-minute interval sensor readings (>= 200).
    output_path : str, optional
        Target CSV file path. If provided, saves the DataFrame to disk.
    seed : int, default=42
        Random seed for reproducible telemetry simulation.

    Returns:
    --------
    pd.DataFrame
        Synthesized dataset with columns:
        [timestamp, pump_id, vibration, temperature, pressure, rpm, flow_rate]
    """
    if n_records < 200:
        n_records = 200

    np.random.seed(seed)

    # 1. Generate Timestamps (5-minute intervals)
    start_time = pd.Timestamp("2026-08-20 06:00:00")
    timestamps = [start_time + pd.Timedelta(minutes=5 * i) for i in range(n_records)]

    pump_id = "Pump P-101"

    # Define normal baseline operational statistics for centrifugal pump
    # Normal phase: 0 to ~80% of records
    # Abnormal phase: last ~20% of records with progressive mechanical & thermal degradation
    normal_count = int(n_records * 0.80)
    abnormal_count = n_records - normal_count

    # --- Phase 1: Normal Operation ---
    # Vibration: nominal 2.2 mm/s RMS (noise ±0.25)
    vib_normal = np.random.normal(loc=2.2, scale=0.25, size=normal_count)
    # Temperature: nominal 58.0 °C (noise ±1.2)
    temp_normal = np.random.normal(loc=58.0, scale=1.2, size=normal_count)
    # Pressure: nominal 6.2 bar (noise ±0.12)
    pres_normal = np.random.normal(loc=6.2, scale=0.12, size=normal_count)
    # RPM: nominal 2950 RPM (noise ±8.0)
    rpm_normal = np.random.normal(loc=2950.0, scale=8.0, size=normal_count)
    # Flow Rate: nominal 115.0 m³/h (noise ±2.0)
    flow_normal = np.random.normal(loc=115.0, scale=2.0, size=normal_count)

    # --- Phase 2: Gradual Abnormal Degradation ---
    # Degradation curves (progressive escalation)
    degradation_curve = np.linspace(0.0, 1.0, abnormal_count) ** 1.5

    # 1. Vibration increases gradually from ~2.4 mm/s up to ~7.8 mm/s (critical breach)
    vib_abnormal = (
        2.4 + (degradation_curve * 5.4) + np.random.normal(loc=0.0, scale=0.35, size=abnormal_count)
    )

    # 2. Temperature increases gradually from ~59.0 °C up to ~88.5 °C (critical breach)
    temp_abnormal = (
        59.0 + (degradation_curve * 29.5) + np.random.normal(loc=0.0, scale=1.5, size=abnormal_count)
    )

    # 3. Pressure decreases gradually from ~6.1 bar down to ~3.5 bar (loss of prime/cavitation)
    pres_abnormal = (
        6.1 - (degradation_curve * 2.6) + np.random.normal(loc=0.0, scale=0.15, size=abnormal_count)
    )

    # 4. Flow rate decreases gradually from ~114.0 m³/h down to ~68.0 m³/h
    flow_abnormal = (
        114.0 - (degradation_curve * 46.0) + np.random.normal(loc=0.0, scale=2.5, size=abnormal_count)
    )

    # 5. RPM remains mostly stable with standard industrial electrical frequency variance
    rpm_abnormal = np.random.normal(loc=2946.0, scale=9.0, size=abnormal_count)

    # Concatenate normal and abnormal telemetry
    vibration = np.concatenate([vib_normal, vib_abnormal]).round(2)
    temperature = np.concatenate([temp_normal, temp_abnormal]).round(2)
    pressure = np.concatenate([pres_normal, pres_abnormal]).round(2)
    rpm = np.concatenate([rpm_normal, rpm_abnormal]).round(1)
    flow_rate = np.concatenate([flow_normal, flow_abnormal]).round(2)

    # Assemble into DataFrame with required column schema
    df = pd.DataFrame({
        "timestamp": [ts.strftime("%Y-%m-%d %H:%M:%S") for ts in timestamps],
        "pump_id": pump_id,
        "vibration": vibration,
        "temperature": temperature,
        "pressure": pressure,
        "rpm": rpm,
        "flow_rate": flow_rate,
    })

    # Save to CSV if requested or default path
    if output_path:
        dest_file = Path(output_path)
        dest_file.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(dest_file, index=False)
        print(f"Successfully generated {len(df)} synthetic telemetry records -> {dest_file}")

    return df


if __name__ == "__main__":
    # Default target: data/raw/pump_p101_sensor_data.csv
    workspace_root = Path(__file__).resolve().parent.parent.parent
    default_csv_path = workspace_root / "data" / "raw" / "pump_p101_sensor_data.csv"
    generate_pump_p101_data(n_records=250, output_path=str(default_csv_path))
