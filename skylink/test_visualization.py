"""
Test script to verify visualization is working correctly with planes and drones visible
"""

import pandas as pd
import numpy as np
from visualization import plot_airspace
from collision_module.collision_detection import detect_collisions
import os
from datetime import datetime

def create_test_data_with_collisions():
    """Create small test dataset that will definitely show planes, drones, and collisions"""
    
    print("Creating test data with guaranteed visibility...")
    
    # Create test planes around NYC area with low altitudes to match drones
    planes_data = []
    base_lat, base_lon = 40.7128, -74.0060  # NYC coordinates
    
    for i in range(5):
        planes_data.append({
            'icao24': f'TEST{i:03d}',
            'callsign': f'UAL{i+100}',
            'latitude': base_lat + (i * 0.02) - 0.04,  # Spread planes out
            'longitude': base_lon + (i * 0.02) - 0.04,
            'baro_altitude': 200 + (i * 50),  # Low altitudes: 200-400m
            'velocity': 150 + (i * 20),
            'origin_country': 'United States'
        })
    
    # Create test drones near the planes to ensure collisions
    drones_data = []
    for i in range(5):
        drones_data.append({
            'drone_id': f'DRONE_{i}',
            'latitude': base_lat + (i * 0.02) - 0.04 + 0.001,  # Very close to planes
            'longitude': base_lon + (i * 0.02) - 0.04 + 0.001,
            'altitude': 180 + (i * 50),  # Close altitude to planes
            'speed': 15 + (i * 2),
            'heading': i * 72,  # Different headings
            'time_step': 1,
            'timestamp': '2025-10-11 20:00:00'
        })
    
    planes_df = pd.DataFrame(planes_data)
    drones_df = pd.DataFrame(drones_data)
    
    print(f"Created {len(planes_df)} test planes and {len(drones_df)} test drones")
    print("Planes locations:")
    for _, plane in planes_df.iterrows():
        print(f"  {plane['callsign']}: ({plane['latitude']:.4f}, {plane['longitude']:.4f}) at {plane['baro_altitude']}m")
    
    print("Drone locations:")
    for _, drone in drones_df.iterrows():
        print(f"  {drone['drone_id']}: ({drone['latitude']:.4f}, {drone['longitude']:.4f}) at {drone['altitude']}m")
    
    return planes_df, drones_df

def test_visualization_with_real_collision_detection():
    """Test the complete system with real collision detection"""
    
    print("="*60)
    print("TESTING SKYLINK VISUALIZATION WITH COLLISION DETECTION")
    print("="*60)
    
    # Create test data
    planes_df, drones_df = create_test_data_with_collisions()
    
    # Run collision detection
    print(f"\nRunning collision detection...")
    alerts = detect_collisions(
        planes_df, 
        drones_df, 
        h_threshold=0.5,  # 500m horizontal
        v_threshold=100   # 100m vertical
    )
    
    print(f"Found {len(alerts)} collision alerts")
    
    # Create the map
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    map_file = f"outputs/test_visualization_{timestamp}.html"
    
    print(f"\nCreating interactive map...")
    success = plot_airspace(planes_df, drones_df, alerts, map_file)
    
    if success:
        print(f"✅ Test map created successfully!")
        print(f"📍 Map location: {os.path.abspath(map_file)}")
        print(f"\n🌐 Opening map in browser...")
        
        # Try to open the map
        try:
            import webbrowser
            webbrowser.open(f'file://{os.path.abspath(map_file)}')
            print("✅ Map should now be open in your default browser!")
        except:
            print(f"💡 Manually open: {os.path.abspath(map_file)}")
        
        # Print summary
        print(f"\n📊 TEST RESULTS:")
        print(f"   Planes on map: {len(planes_df)}")
        print(f"   Drones on map: {len(drones_df)}")
        print(f"   Collision alerts: {len(alerts)}")
        print(f"   Map file: {map_file}")
        
        if alerts:
            print(f"\n⚠️  COLLISION DETAILS:")
            for i, alert in enumerate(alerts, 1):
                print(f"   {i}. Drone {alert['drone_id']} vs Plane {alert['plane_icao24']}")
                print(f"      Distance: {alert['horizontal_distance']:.3f} km horizontal, {alert['vertical_distance']:.1f} m vertical")
        
        return True
    else:
        print("❌ Failed to create map")
        return False

def create_simple_test_map():
    """Create a very simple test map with just a few markers"""
    
    print("\nCreating simple test map...")
    
    # Simple test data - just 2 planes and 2 drones in NYC
    planes_data = [{
        'icao24': 'PLANE1',
        'callsign': 'TEST1',
        'latitude': 40.7128,
        'longitude': -74.0060,
        'baro_altitude': 300,
        'velocity': 200,
        'origin_country': 'United States'
    }, {
        'icao24': 'PLANE2',  
        'callsign': 'TEST2',
        'latitude': 40.7200,
        'longitude': -74.0000,
        'baro_altitude': 400,
        'velocity': 180,
        'origin_country': 'United States'
    }]
    
    drones_data = [{
        'drone_id': 'DRONE1',
        'latitude': 40.7150,
        'longitude': -74.0030,
        'altitude': 150,
        'speed': 20,
        'heading': 90,
        'time_step': 1,
        'timestamp': '2025-10-11 20:00:00'
    }, {
        'drone_id': 'DRONE2',
        'latitude': 40.7180,
        'longitude': -73.9980,
        'altitude': 180,
        'speed': 25,
        'heading': 180,
        'time_step': 1,
        'timestamp': '2025-10-11 20:00:00'
    }]
    
    planes_df = pd.DataFrame(planes_data)
    drones_df = pd.DataFrame(drones_data)
    
    # No alerts for this simple test
    alerts = []
    
    # Create map
    map_file = "outputs/simple_test_map.html"
    plot_airspace(planes_df, drones_df, alerts, map_file)
    
    print(f"Simple test map created: {map_file}")
    
    # Open it
    try:
        import webbrowser
        webbrowser.open(f'file://{os.path.abspath(map_file)}')
        print("✅ Simple map opened in browser!")
    except:
        print(f"💡 Manually open: {os.path.abspath(map_file)}")

def main():
    """Run all visualization tests"""
    
    print("🚁✈️ SkyLink Visualization Testing")
    print("="*50)
    
    # Test 1: Simple map
    create_simple_test_map()
    
    # Test 2: Full collision detection test
    success = test_visualization_with_real_collision_detection()
    
    if success:
        print("\n" + "="*60)
        print("🎉 ALL VISUALIZATION TESTS COMPLETED SUCCESSFULLY!")
        print("="*60)
        print("✅ Planes should appear as blue airplane icons")
        print("✅ Drones should appear as green helicopter icons")
        print("✅ Collision alerts should appear as red warning icons")
        print("✅ Maps should be interactive with clickable popups")
        print(f"✅ All test files saved in: {os.path.abspath('outputs')}")
    else:
        print("\n❌ Some tests failed. Check error messages above.")

if __name__ == "__main__":
    main()