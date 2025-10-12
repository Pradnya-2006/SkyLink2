#!/usr/bin/env python3
"""
Drone Dashboard Demo
Demonstrates the drone alert system and dashboard visualization.
This script shows how to integrate the new drone alert system with existing SkyLink data.
"""

import sys
import os
import pandas as pd
from datetime import datetime

# Add the parent directory to sys.path to import existing modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import existing SkyLink modules
try:
    from collision_module.collision_detection import detect_collisions, get_collision_summary
    from drone_alerts.drone_dashboard import DroneDashboard
    from drone_alerts.alert_translator import DroneAlertTranslator
except ImportError as e:
    print(f"Error importing modules: {e}")
    print("Make sure you're running this from the skylink directory")
    sys.exit(1)

def load_sample_data():
    """Load sample drone and plane data"""
    
    # Load drone data
    drone_file = "drone_data/dummy_drone_dataset_30.csv"
    plane_file = "plane_data/opensky_live_states.csv"
    
    try:
        # Load drone data
        drone_df = pd.read_csv(drone_file)
        print(f"✅ Loaded {len(drone_df)} drone records")
        
        # Load plane data  
        plane_df = pd.read_csv(plane_file)
        print(f"✅ Loaded {len(plane_df)} plane records")
        
        return drone_df, plane_df
        
    except FileNotFoundError as e:
        print(f"❌ Error loading data files: {e}")
        print("Please ensure the data files exist in drone_data/ and plane_data/ directories")
        return None, None

def prepare_data_for_dashboard(drone_df, plane_df):
    """Convert dataframe data to format expected by dashboard"""
    
    # Convert drone data to dictionary format
    drone_data = []
    for _, row in drone_df.iterrows():
        drone_dict = {
            'drone_id': row.get('drone_id', f"drone_{_}"),
            'latitude': float(row.get('latitude', 0)),
            'longitude': float(row.get('longitude', 0)),
            'altitude': float(row.get('altitude', 0)),
            'speed': float(row.get('speed', 0)),
            'heading': float(row.get('heading', 0)),
            'timestamp': row.get('timestamp', datetime.now().isoformat())
        }
        drone_data.append(drone_dict)
    
    # Convert plane data to dictionary format (handle the actual column names)
    plane_data = []
    for _, row in plane_df.iterrows():
        # Handle missing or NaN values
        if pd.isna(row.get('latitude')) or pd.isna(row.get('longitude')):
            continue  # Skip planes with missing location data
            
        plane_dict = {
            'callsign': str(row.get('callsign', f"aircraft_{_}")).strip(),
            'icao24': row.get('icao24', f"unknown_{_}"),
            'latitude': float(row.get('latitude', 0)),
            'longitude': float(row.get('longitude', 0)),
            'altitude': float(row.get('baro_altitude', 0)) if not pd.isna(row.get('baro_altitude')) else 0,
            'velocity': float(row.get('velocity', 0)) if not pd.isna(row.get('velocity')) else 0,
            'heading': float(row.get('true_track', 0)) if not pd.isna(row.get('true_track')) else 0,
            'timestamp': row.get('time_position', datetime.now().timestamp())
        }
        plane_data.append(plane_dict)
    
    print(f"✅ Prepared {len(drone_data)} drones and {len(plane_data)} planes (filtered from {len(plane_df)} total planes)")
    return drone_data, plane_data

def demo_alert_translator():
    """Demonstrate the alert translator functionality"""
    
    print("\n🔄 Testing Alert Translator...")
    
    # Create sample data
    sample_drone = {
        'drone_id': 'DEMO_DRONE_001',
        'latitude': 12.9716,
        'longitude': 77.5946,
        'altitude': 100
    }
    
    sample_plane = {
        'callsign': 'TEST_AIRCRAFT',
        'latitude': 12.9720,  # Very close to drone
        'longitude': 77.5950,
        'altitude': 150,
        'velocity': 250,
        'heading': 45
    }
    
    translator = DroneAlertTranslator()
    alert = translator.translate_plane_to_drone_alert(sample_plane, sample_drone)
    
    print(f"Alert Level: {alert['danger_level']}")
    print(f"Distance: {alert['distance_km']} km")
    print(f"Guidance: {alert['guidance']}")
    print(f"Color Code: {alert['color_code']}")

def main():
    """Main demo function"""
    
    print("🛰️ SkyLink Drone Dashboard Demo")
    print("=" * 50)
    
    # Check if required packages are available
    try:
        import pandas as pd
        import webbrowser
    except ImportError as e:
        print(f"❌ Missing required package: {e}")
        print("Please install pandas: pip3 install pandas")
        return
    
    # Test alert translator first
    demo_alert_translator()
    
    # Load actual data
    print("\n📊 Loading Data...")
    drone_df, plane_df = load_sample_data()
    
    if drone_df is None or plane_df is None:
        print("❌ Cannot proceed without data files")
        return
    
    # Prepare data for dashboard
    print("\n🔄 Preparing Data for Dashboard...")
    drone_data, plane_data = prepare_data_for_dashboard(drone_df, plane_df)
    
    print(f"✅ Prepared {len(drone_data)} drones and {len(plane_data)} planes for analysis")
    
    # Create dashboard
    print("\n🎛️ Generating Drone Dashboard...")
    dashboard = DroneDashboard()
    
    try:
        dashboard_file, alerts_data = dashboard.generate_dashboard(
            drone_data=drone_data,
            plane_data=plane_data,
            output_dir="outputs"
        )
        
        print("\n📈 Dashboard Statistics:")
        total_alerts = sum(drone['alert_count'] for drone in alerts_data)
        critical_alerts = sum(1 for drone in alerts_data for alert in drone['alerts'] if alert['danger_level'] == 'CRITICAL')
        high_alerts = sum(1 for drone in alerts_data for alert in drone['alerts'] if alert['danger_level'] == 'HIGH')
        
        print(f"   📊 Total Drones: {len(alerts_data)}")
        print(f"   🚨 Total Alerts: {total_alerts}")
        print(f"   🔴 Critical Alerts: {critical_alerts}")
        print(f"   🟠 High Priority Alerts: {high_alerts}")
        
        print(f"\n✅ Dashboard created successfully!")
        print(f"📁 File saved: {dashboard_file}")
        print(f"🌐 Dashboard should open automatically in your browser")
        
        # Show some sample alerts
        if alerts_data and alerts_data[0]['alerts']:
            print(f"\n🔍 Sample Alert Details:")
            sample_alert = alerts_data[0]['alerts'][0]
            print(f"   Drone: {alerts_data[0]['drone_id']}")
            print(f"   Aircraft: {sample_alert['plane_info']['callsign']}")
            print(f"   Distance: {sample_alert['distance_km']} km")
            print(f"   Level: {sample_alert['danger_level']}")
            print(f"   Guidance: {sample_alert['guidance']}")
        
    except Exception as e:
        print(f"❌ Error generating dashboard: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()