"""
Quick test script for the pilot dashboard with voice alert controls.
This will start the dashboard with the test collision scenario.
"""

import os
import sys
import webbrowser
import time
from pathlib import Path

def main():
    print("🚁✈️ SkyLink Pilot Dashboard - Voice Alert Test")
    print("=" * 50)
    
    dashboard_dir = Path(__file__).parent
    
    print("Voice Alert Features:")
    print("✓ Maximum 2 repeats per alert")
    print("✓ 30-second cooldown between same alerts")
    print("✓ 'Clear Voice' button to stop/reset alerts")
    print("✓ Voice status tracking in left panel")
    print("✓ Test collision scenario loaded by default")
    print("")
    
    print("How to test:")
    print("1. Dashboard will load with test collision scenario")
    print("2. Critical/High threat voice alerts will play maximum 2 times")
    print("3. Use 'Clear Voice' button to stop and reset alerts")
    print("4. Toggle 'Voice Alerts' to enable/disable")
    print("5. Use 'Test Mode' button to switch between real/test data")
    print("")
    
    print("Starting dashboard server...")
    print("Dashboard will open at: http://localhost:5000")
    print("")
    print("Press Ctrl+C to stop the server")
    print("=" * 50)
    
    try:
        # Change to dashboard directory
        os.chdir(dashboard_dir)
        
        # Try to open browser after a short delay
        def open_browser():
            time.sleep(2)
            try:
                webbrowser.open('http://localhost:5000')
                print("✓ Dashboard opened in browser")
            except:
                print("⚠ Could not auto-open browser. Please visit http://localhost:5000")
        
        # Start browser opener in background
        import threading
        browser_thread = threading.Thread(target=open_browser)
        browser_thread.daemon = True
        browser_thread.start()
        
        # Import and run Flask app
        from app import app, dashboard_service
        
        print(f"✓ Test data loaded: {len(dashboard_service.planes_df)} planes, {len(dashboard_service.drones_df)} drones")
        print(f"✓ Using test collision scenario: {dashboard_service.use_test_data}")
        
        # Run the Flask app
        app.run(debug=False, host='0.0.0.0', port=5000)
        
    except KeyboardInterrupt:
        print("\n\nDashboard stopped by user")
        
    except ImportError as e:
        print(f"\nERROR: Missing dependencies: {e}")
        print("Please install Flask: pip install flask")
        
    except Exception as e:
        print(f"\nERROR: {e}")

if __name__ == "__main__":
    main()