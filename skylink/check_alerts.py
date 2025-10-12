import json

# Load and display alert data
with open('outputs/drone_alerts_20251012_111045.json', encoding='utf-8') as f:
    data = json.load(f)

print(f"Total drones with alerts: {len(data)}")

# Count alert levels
critical_count = sum(1 for drone in data if drone['highest_priority'] == 'CRITICAL')
high_count = sum(1 for drone in data if drone['highest_priority'] == 'HIGH')
medium_count = sum(1 for drone in data if drone['highest_priority'] == 'MEDIUM')
low_count = sum(1 for drone in data if drone['highest_priority'] == 'LOW')

print(f"Critical alerts: {critical_count}")
print(f"High alerts: {high_count}")
print(f"Medium alerts: {medium_count}")
print(f"Low alerts: {low_count}")

print("\nDetailed Sample Alerts:")
for i, drone_alert in enumerate(data[:5]):
    if drone_alert['alerts']:  # Only show drones with actual alerts
        print(f"\nDrone {drone_alert['drone_id']}:")
        print(f"  Location: {drone_alert['location']}")
        print(f"  Altitude: {drone_alert['altitude']} m")
        print(f"  Total alerts: {drone_alert['alert_count']}")
        print(f"  Highest priority: {drone_alert['highest_priority']}")
        
        for j, alert in enumerate(drone_alert['alerts'][:2]):  # Show first 2 alerts per drone
            print(f"    Alert {j+1}:")
            print(f"      Aircraft: {alert['plane_info']['callsign']}")
            print(f"      Distance: {alert['distance_km']} km")
            print(f"      Level: {alert['danger_level']}")
            print(f"      Guidance: {alert['guidance'][:50]}...")