"""
Pump P-101 Industrial Sensor Analytics Package.
SIH26117.
"""

from analytics.main import analyze_sensor_data
from analytics.data.generate_demo_data import generate_pump_p101_data
from analytics.config import (
    DEFAULT_EQUIPMENT_ID,
    SENSOR_THRESHOLDS,
    HEALTH_WEIGHTS,
    SYSTEM_LIMITATIONS,
)

__all__ = [
    "analyze_sensor_data",
    "generate_pump_p101_data",
    "DEFAULT_EQUIPMENT_ID",
    "SENSOR_THRESHOLDS",
    "HEALTH_WEIGHTS",
    "SYSTEM_LIMITATIONS",
]
