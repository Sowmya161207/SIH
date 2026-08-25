"""
Data validation and preprocessing module for Pump P-101 sensor telemetry.
Ensures schema adherence, data type correctness, handles missing values,
and prepares raw telemetry for analytics.
"""

from typing import Union, List, Dict, Any
from pathlib import Path
import pandas as pd
import numpy as np

from analytics.config import REQUIRED_COLUMNS, SENSOR_COLUMNS, DEFAULT_EQUIPMENT_ID


def validate_and_prepare_data(
    data: Union[pd.DataFrame, List[Dict[str, Any]], Dict[str, List[Any]], str, Path]
) -> pd.DataFrame:
    """
    Validates, cleans, and standardizes input sensor telemetry.

    Parameters:
    -----------
    data : pd.DataFrame | list[dict] | dict[str, list] | str | Path
        Raw sensor telemetry dataset or path to CSV file.

    Returns:
    --------
    pd.DataFrame
        Cleaned, type-casted, and validated DataFrame sorted by timestamp.

    Raises:
    -------
    ValueError
        If required columns are missing, data is empty, or format is invalid.
    """
    # 1. Load data into DataFrame based on type
    if isinstance(data, (str, Path)):
        file_path = Path(data)
        if not file_path.exists():
            raise ValueError(f"Sensor data file not found: {file_path}")
        df = pd.read_csv(file_path)
    elif isinstance(data, list):
        if len(data) == 0:
            raise ValueError("Input sensor telemetry list is empty.")
        df = pd.DataFrame(data)
    elif isinstance(data, dict):
        df = pd.DataFrame(data)
    elif isinstance(data, pd.DataFrame):
        df = data.copy()
    else:
        raise ValueError(
            f"Unsupported data format: {type(data)}. Expected DataFrame, list of dicts, or CSV path."
        )

    if df.empty:
        raise ValueError("Sensor dataset is empty. At least 5 rows are required for time-series analytics.")

    # 2. Check required columns
    missing_cols = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing_cols:
        raise ValueError(
            f"Missing required columns in sensor telemetry: {missing_cols}. "
            f"Expected schema must include: {REQUIRED_COLUMNS}"
        )

    # 3. Minimum row count check
    if len(df) < 5:
        raise ValueError(
            f"Insufficient data points ({len(df)} rows). A minimum of 5 records is required for moving average analytics."
        )

    # 4. Standardize types
    df = df.copy()

    # Normalize pump_id (fill default if null)
    df["pump_id"] = df["pump_id"].fillna(DEFAULT_EQUIPMENT_ID).astype(str)

    # Timestamp conversion and sorting
    try:
        df["timestamp"] = pd.to_datetime(df["timestamp"])
    except Exception as e:
        raise ValueError(f"Failed to parse 'timestamp' column into valid datetime format: {e}")

    df = df.sort_values("timestamp").reset_index(drop=True)

    # Cast numeric sensor columns and handle nulls
    for col in SENSOR_COLUMNS:
        df[col] = pd.to_numeric(df[col], errors="coerce")
        
        # Handle nulls / NaN via forward fill, backward fill, and median fallback
        if df[col].isnull().any():
            df[col] = df[col].ffill().bfill()
            if df[col].isnull().any():
                df[col] = df[col].fillna(0.0)

    return df
