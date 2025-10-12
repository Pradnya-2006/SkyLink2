"""
Drone Alerts Module
Handles translation of plane data into drone-readable alerts and dashboard visualization.
"""

from .alert_translator import DroneAlertTranslator
from .drone_dashboard import DroneDashboard

__all__ = ['DroneAlertTranslator', 'DroneDashboard']