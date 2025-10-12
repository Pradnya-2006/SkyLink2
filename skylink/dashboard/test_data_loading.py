"""
Test script to verify data loading for both test and real scenarios.
"""

import sys
import os
sys.path.append('..')

from app import PilotDashboardService

def test_data_loading():
    print("🚁✈️ Testing SkyLink Data Loading")
    print("=" * 50)
    
    # Create dashboard service
    service = PilotDashboardService()
    
    print("\n📊 DATA LOADING RESULTS:")
    print(f"Test Planes: {len(service.test_planes_df)}")
    print(f"Test Drones: {len(service.test_drones_df)}")
    print(f"Real Planes: {len(service.real_planes_df)}")
    print(f"Real Drones: {len(service.real_drones_df)}")
    
    print(f"\nCurrent Mode: {'TEST' if service.use_test_data else 'REAL'}")
    print(f"Current Planes: {len(service.planes_df)}")
    print(f"Current Drones: {len(service.drones_df)}")
    
    # Test current aircraft
    current_aircraft = service.get_current_aircraft()
    if current_aircraft:
        print(f"\n✈️ CURRENT AIRCRAFT:")
        print(f"Callsign: {current_aircraft['callsign']}")
        print(f"Position: ({current_aircraft['latitude']:.4f}, {current_aircraft['longitude']:.4f})")
        print(f"Altitude: {current_aircraft['altitude']} m")
        print(f"Speed: {current_aircraft['speed']} m/s")
    else:
        print("\n❌ No current aircraft found!")
    
    # Test nearby aircraft
    if current_aircraft:
        nearby = service.get_nearby_aircraft(current_aircraft, 50)  # 50 NM range
        print(f"\n🛩️ NEARBY AIRCRAFT (within 50 NM): {len(nearby)}")
        for aircraft in nearby[:3]:  # Show first 3
            print(f"  {aircraft['callsign']}: {aircraft['distance']:.1f} NM away")
        
        # Test nearby drones
        nearby_drones = service.get_nearby_drones(current_aircraft, 50)
        print(f"\n🚁 NEARBY DRONES (within 50 NM): {len(nearby_drones)}")
        for drone in nearby_drones[:3]:  # Show first 3
            print(f"  {drone['drone_id']}: {drone['distance']:.1f} NM away")
        
        # Test collision threats
        threats = service.get_collision_threats(current_aircraft, 50)
        print(f"\n⚠️ COLLISION THREATS: {len(threats)}")
        for threat in threats[:3]:  # Show first 3
            print(f"  {threat['id']}: {threat['horizontal_distance']:.3f} km, {threat['risk_level']} risk")
    
    print("\n" + "=" * 50)
    
    # Test switching modes
    print("\n🔄 TESTING MODE SWITCH...")
    
    service.use_test_data = not service.use_test_data
    service.switch_data_mode()
    
    print(f"Switched to: {'TEST' if service.use_test_data else 'REAL'}")
    print(f"Current Planes: {len(service.planes_df)}")
    print(f"Current Drones: {len(service.drones_df)}")
    
    current_aircraft = service.get_current_aircraft()
    if current_aircraft:
        print(f"New Current Aircraft: {current_aircraft['callsign']} at ({current_aircraft['latitude']:.4f}, {current_aircraft['longitude']:.4f})")
    
    print("\n✅ Data loading test completed!")

if __name__ == "__main__":
    test_data_loading()