"""
Analyze the actual user dataset to understand geographic distribution
"""

import pandas as pd
import numpy as np

def analyze_user_dataset():
    """Analyze the user's actual plane and drone data"""
    
    print("🔍 ANALYZING YOUR ACTUAL DATASET")
    print("="*50)
    
    # Load actual data
    planes_df = pd.read_csv('plane_data/opensky_live_states.csv')
    drones_df = pd.read_csv('drone_data/dummy_drone_dataset_30.csv')
    
    print(f"📊 DATASET SUMMARY:")
    print(f"   Planes: {len(planes_df):,} records")
    print(f"   Drones: {len(drones_df):,} records")
    
    # Analyze plane distribution
    print(f"\n✈️ PLANE DATA ANALYSIS:")
    print(f"   Countries: {planes_df['origin_country'].nunique()} different countries")
    print(f"   Top countries:")
    country_counts = planes_df['origin_country'].value_counts().head(5)
    for country, count in country_counts.items():
        print(f"      {country}: {count} planes")
    
    # Geographic bounds for planes
    plane_lat_min, plane_lat_max = planes_df['latitude'].min(), planes_df['latitude'].max()
    plane_lon_min, plane_lon_max = planes_df['longitude'].min(), planes_df['longitude'].max()
    
    print(f"   Geographic coverage:")
    print(f"      Latitude: {plane_lat_min:.2f} to {plane_lat_max:.2f}")
    print(f"      Longitude: {plane_lon_min:.2f} to {plane_lon_max:.2f}")
    
    # Analyze drone distribution  
    print(f"\n🚁 DRONE DATA ANALYSIS:")
    print(f"   Unique drones: {drones_df['drone_id'].nunique()}")
    print(f"   Time steps: {drones_df['time_step'].nunique()}")
    
    # Geographic bounds for drones
    drone_lat_min, drone_lat_max = drones_df['latitude'].min(), drones_df['latitude'].max()
    drone_lon_min, drone_lon_max = drones_df['longitude'].min(), drones_df['longitude'].max()
    
    print(f"   Geographic coverage:")
    print(f"      Latitude: {drone_lat_min:.2f} to {drone_lat_max:.2f}")
    print(f"      Longitude: {drone_lon_min:.2f} to {drone_lon_max:.2f}")
    
    # Identify probable location
    if 12 <= drone_lat_min <= 13 and 77 <= drone_lon_min <= 78:
        print(f"   🌍 Location: Appears to be Bangalore, India region")
    
    # Check for geographic overlap
    print(f"\n🗺️ GEOGRAPHIC OVERLAP ANALYSIS:")
    
    # Find planes in India/nearby region
    india_bounds = {
        'min_lat': drone_lat_min - 1, 'max_lat': drone_lat_max + 1,
        'min_lon': drone_lon_min - 1, 'max_lon': drone_lon_max + 1
    }
    
    planes_in_drone_area = planes_df[
        (planes_df['latitude'] >= india_bounds['min_lat']) &
        (planes_df['latitude'] <= india_bounds['max_lat']) &
        (planes_df['longitude'] >= india_bounds['min_lon']) &
        (planes_df['longitude'] <= india_bounds['max_lon'])
    ]
    
    print(f"   Planes near drone area: {len(planes_in_drone_area)}")
    
    if len(planes_in_drone_area) > 0:
        print(f"   ✅ Found planes in drone region!")
        print(f"   Plane details:")
        for _, plane in planes_in_drone_area.head(3).iterrows():
            print(f"      {plane['callsign']} ({plane['origin_country']}) at {plane['latitude']:.3f}, {plane['longitude']:.3f}")
    else:
        print(f"   ❌ No planes found in drone area")
        print(f"   Closest planes:")
        # Find closest planes by calculating distance to drone center
        drone_center_lat = drones_df['latitude'].mean()
        drone_center_lon = drones_df['longitude'].mean()
        
        planes_df['distance_to_drones'] = np.sqrt(
            (planes_df['latitude'] - drone_center_lat)**2 + 
            (planes_df['longitude'] - drone_center_lon)**2
        )
        
        closest_planes = planes_df.nsmallest(3, 'distance_to_drones')
        for _, plane in closest_planes.iterrows():
            print(f"      {plane['callsign']} ({plane['origin_country']}) at {plane['latitude']:.3f}, {plane['longitude']:.3f} - {plane['distance_to_drones']:.2f}° away")
    
    # Altitude analysis
    print(f"\n📏 ALTITUDE ANALYSIS:")
    print(f"   Plane altitudes: {planes_df['baro_altitude'].min():.0f}m to {planes_df['baro_altitude'].max():.0f}m")
    print(f"   Drone altitudes: {drones_df['altitude'].min():.0f}m to {drones_df['altitude'].max():.0f}m")
    
    # Overlap in altitude
    low_altitude_planes = planes_df[planes_df['baro_altitude'] <= drones_df['altitude'].max()]
    print(f"   Planes at drone altitude levels: {len(low_altitude_planes)}")
    
    return planes_df, drones_df, planes_in_drone_area

if __name__ == "__main__":
    analyze_user_dataset()