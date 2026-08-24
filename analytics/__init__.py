"""
Pump P-101 Industrial Sensor & Incident Intelligence Package.
SIH PS 26117.

Provides callable industrial intelligence tools for the Planner:
- analyze_equipment(...)
- investigate_incident(...)
- predict_maintenance_risk(...)
- analyze_sensor_data(...)
"""

from analytics.main import analyze_sensor_data
from analytics.intelligence import (
    analyze_equipment,
    investigate_incident,
    predict_maintenance_risk,
)
from analytics.data.generate_demo_data import generate_pump_p101_data
from analytics.config import (
    DEFAULT_EQUIPMENT_ID,
    SENSOR_THRESHOLDS,
    HEALTH_WEIGHTS,
    SYSTEM_LIMITATIONS,
)

__all__ = [
    "analyze_sensor_data",
    "analyze_equipment",
    "investigate_incident",
    "predict_maintenance_risk",
    "generate_pump_p101_data",
    "DEFAULT_EQUIPMENT_ID",
    "SENSOR_THRESHOLDS",
    "HEALTH_WEIGHTS",
    "SYSTEM_LIMITATIONS",
]
