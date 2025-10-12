"""
Alert Translator Module
Converts plane detection data into drone-readable alerts with guidance and prioritization.
"""

import json
import math
from datetime import datetime
from typing import List, Dict, Tuple

class DroneAlertTranslator:
    def __init__(self):
        self.danger_thresholds = {
            'critical': 0.5,  # km
            'high': 1.0,      # km
            'medium': 2.0,    # km
            'low': 5.0        # km
        }
        
    def translate_plane_to_drone_alert(self, plane_data: Dict, drone_data: Dict) -> Dict:
        """Convert plane detection data into drone-readable alerts"""
        distance = self._calculate_distance(plane_data, drone_data)
        danger_level = self._get_danger_level(distance)
        guidance = self._generate_guidance(plane_data, drone_data, danger_level)
        
        return {
            'alert_id': f"alert_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{plane_data.get('callsign', 'unknown')}",
            'timestamp': datetime.now().isoformat(),
            'danger_level': danger_level,
            'distance_km': round(distance, 2),
            'plane_info': {
                'callsign': plane_data.get('callsign', 'Unknown'),
                'altitude': plane_data.get('altitude', 0),
                'speed': plane_data.get('velocity', 0),
                'heading': plane_data.get('heading', 0)
            },
            'drone_info': {
                'id': drone_data.get('drone_id'),
                'altitude': drone_data.get('altitude', 0),
                'location': [drone_data.get('latitude'), drone_data.get('longitude')]
            },
            'guidance': guidance,
            'priority': self._get_priority(danger_level),
            'color_code': self._get_color_code(danger_level)
        }
    
    def process_multiple_alerts(self, drone_data: List[Dict], plane_data: List[Dict]) -> List[Dict]:
        """Process alerts for multiple drones and planes"""
        all_alerts = []
        
        for drone in drone_data:
            drone_alerts = []
            
            for plane in plane_data:
                alert = self.translate_plane_to_drone_alert(plane, drone)
                if alert['danger_level'] != 'SAFE':  # Only include actual alerts
                    drone_alerts.append(alert)
            
            # Sort alerts by priority for this drone
            drone_alerts.sort(key=lambda x: x['priority'])
            
            # Add drone summary
            drone_summary = {
                'drone_id': drone.get('drone_id'),
                'location': [drone.get('latitude'), drone.get('longitude')],
                'altitude': drone.get('altitude', 0),
                'alerts': drone_alerts,
                'alert_count': len(drone_alerts),
                'highest_priority': drone_alerts[0]['danger_level'] if drone_alerts else 'SAFE'
            }
            
            all_alerts.append(drone_summary)
            
        return all_alerts
    
    def _calculate_distance(self, plane_data: Dict, drone_data: Dict) -> float:
        """Calculate distance between plane and drone using Haversine formula"""
        lat1, lon1 = plane_data.get('latitude', 0), plane_data.get('longitude', 0)
        lat2, lon2 = drone_data.get('latitude', 0), drone_data.get('longitude', 0)
        
        # Haversine formula
        R = 6371  # Earth's radius in km
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        return R * c
    
    def _get_danger_level(self, distance: float) -> str:
        """Determine danger level based on distance"""
        if distance <= self.danger_thresholds['critical']:
            return 'CRITICAL'
        elif distance <= self.danger_thresholds['high']:
            return 'HIGH'
        elif distance <= self.danger_thresholds['medium']:
            return 'MEDIUM'
        elif distance <= self.danger_thresholds['low']:
            return 'LOW'
        else:
            return 'SAFE'
    
    def _generate_guidance(self, plane_data: Dict, drone_data: Dict, danger_level: str) -> str:
        """Generate safe guidance text for drone"""
        guidance_map = {
            'CRITICAL': "⚠️ IMMEDIATE ACTION REQUIRED: Descend to safe altitude and move away from flight path!",
            'HIGH': "🚨 HIGH ALERT: Adjust altitude and maintain safe distance from aircraft",
            'MEDIUM': "⚡ CAUTION: Monitor aircraft movement and be prepared to take evasive action",
            'LOW': "📡 ADVISORY: Aircraft detected in area, maintain awareness",
            'SAFE': "✅ CLEAR: No immediate threats detected"
        }
        return guidance_map.get(danger_level, "Monitor surroundings")
    
    def _get_priority(self, danger_level: str) -> int:
        """Get priority ranking for alert sorting (1 = highest priority)"""
        priority_map = {'CRITICAL': 1, 'HIGH': 2, 'MEDIUM': 3, 'LOW': 4, 'SAFE': 5}
        return priority_map.get(danger_level, 5)
    
    def _get_color_code(self, danger_level: str) -> str:
        """Get color code for dashboard display"""
        color_map = {
            'CRITICAL': '#FF0000',  # Red
            'HIGH': '#FF6600',      # Orange  
            'MEDIUM': '#FFFF00',    # Yellow
            'LOW': '#00FF00',       # Green
            'SAFE': '#00AA00'       # Dark Green
        }
        return color_map.get(danger_level, '#808080')
    
    def export_alerts_json(self, alerts_data: List[Dict], output_path: str) -> str:
        """Export alerts data to JSON file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"drone_alerts_{timestamp}.json"
        filepath = f"{output_path}/{filename}"
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(alerts_data, f, indent=2, ensure_ascii=False)
            
        return filepath