"""
SkyLink Pilot Dashboard Launcher

Quick launcher script for the pilot dashboard.
Run this to start the dashboard server.
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    print("=" * 60)
    print("SKYLINK PILOT DASHBOARD LAUNCHER")
    print("=" * 60)
    
    # Get the dashboard directory
    dashboard_dir = Path(__file__).parent
    
    print(f"Dashboard directory: {dashboard_dir}")
    print(f"Current working directory: {os.getcwd()}")
    
    # Check if required files exist
    app_file = dashboard_dir / "app.py"
    template_file = dashboard_dir / "templates" / "pilot_dashboard.html"
    
    if not app_file.exists():
        print(f"ERROR: app.py not found at {app_file}")
        return False
        
    if not template_file.exists():
        print(f"ERROR: pilot_dashboard.html not found at {template_file}")
        return False
    
    print("✓ Required files found")
    
    # Check data files
    data_dir = dashboard_dir.parent
    plane_data = data_dir / "plane_data" / "opensky_live_states.csv"
    drone_data = data_dir / "drone_data" / "dummy_drone_dataset_30.csv"
    
    if plane_data.exists():
        print(f"✓ Plane data found: {plane_data}")
    else:
        print(f"⚠ Plane data not found: {plane_data}")
        
    if drone_data.exists():
        print(f"✓ Drone data found: {drone_data}")
    else:
        print(f"⚠ Drone data not found: {drone_data}")
    
    print("\nStarting Flask server...")
    print("Dashboard will be available at: http://localhost:5000")
    print("Press Ctrl+C to stop the server")
    print("-" * 60)
    
    try:
        # Change to dashboard directory
        os.chdir(dashboard_dir)
        
        # Run the Flask app
        subprocess.run([sys.executable, "app.py"], check=True)
        
    except KeyboardInterrupt:
        print("\n\nDashboard stopped by user")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"\nERROR: Flask server failed to start: {e}")
        return False
        
    except Exception as e:
        print(f"\nERROR: Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = main()
    if not success:
        input("\nPress Enter to exit...")