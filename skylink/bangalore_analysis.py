"""
Run collision detection specifically for the Bangalore, India region 
where the user's drones are located
"""

import pandas as pd
from collision_module.collision_detection import detect_collisions
from visualization import plot_airspace
from datetime import datetime
import os

def run_bangalore_analysis():
    """Run collision detection for Bangalore region with user's actual data"""
    
    print("🇮🇳 BANGALORE REGION COLLISION ANALYSIS")
    print("="*50)
    print("Using YOUR actual OpenSky plane data + drone data")
    
    # Load YOUR actual data
    planes_df = pd.read_csv('plane_data/opensky_live_states.csv')
    drones_df = pd.read_csv('drone_data/dummy_drone_dataset_30.csv')
    
    print(f"Loaded: {len(planes_df):,} planes, {len(drones_df)} drones")
    
    # Filter planes to Bangalore region (where your drones are)
    bangalore_bounds = {
        'min_lat': 12.5, 'max_lat': 13.5,  # Expanded around Bangalore
        'min_lon': 77.0, 'max_lon': 78.0
    }
    
    bangalore_planes = planes_df[
        (planes_df['latitude'] >= bangalore_bounds['min_lat']) &
        (planes_df['latitude'] <= bangalore_bounds['max_lat']) &
        (planes_df['longitude'] >= bangalore_bounds['min_lon']) &
        (planes_df['longitude'] <= bangalore_bounds['max_lon'])
    ].copy()
    
    print(f"Planes in Bangalore region: {len(bangalore_planes)}")
    
    if len(bangalore_planes) == 0:
        print("⚠️ No planes found in exact drone region. Expanding search...")
        # Expand search area
        expanded_bounds = {
            'min_lat': 10.0, 'max_lat': 15.0,
            'min_lon': 75.0, 'max_lon': 80.0
        }
        
        bangalore_planes = planes_df[
            (planes_df['latitude'] >= expanded_bounds['min_lat']) &
            (planes_df['latitude'] <= expanded_bounds['max_lat']) &
            (planes_df['longitude'] >= expanded_bounds['min_lon']) &
            (planes_df['longitude'] <= expanded_bounds['max_lon'])
        ].copy()
        
        print(f"Planes in expanded South India region: {len(bangalore_planes)}")
    
    if len(bangalore_planes) > 0:
        print(f"\n✈️ Found planes in the region:")
        for _, plane in bangalore_planes.head(5).iterrows():
            print(f"   {plane['callsign'].strip()} ({plane['origin_country']}) - "
                  f"Alt: {plane['baro_altitude']:.0f}m at "
                  f"({plane['latitude']:.3f}, {plane['longitude']:.3f})")
    
    print(f"\n🚁 Your drones:")
    unique_drones = drones_df.drop_duplicates('drone_id')
    for _, drone in unique_drones.head(5).iterrows():
        print(f"   {drone['drone_id']} - Alt: {drone['altitude']:.0f}m at "
              f"({drone['latitude']:.3f}, {drone['longitude']:.3f})")
    
    # Run collision detection
    print(f"\n🔍 Running collision detection...")
    print(f"   Thresholds: 2.0 km horizontal, 200 m vertical")
    
    alerts = detect_collisions(
        bangalore_planes, 
        drones_df, 
        h_threshold=2.0,  # 2km - more relaxed for regional analysis
        v_threshold=200   # 200m - relaxed vertical threshold
    )
    
    print(f"   Found {len(alerts)} potential collisions")
    
    # Create visualization
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    map_file = f"outputs/bangalore_analysis_{timestamp}.html"
    
    print(f"\n🗺️ Creating map for Bangalore region...")
    plot_airspace(bangalore_planes, drones_df, alerts, map_file)
    
    # Open the map
    try:
        import webbrowser
        webbrowser.open(f'file://{os.path.abspath(map_file)}')
        print(f"✅ Map opened in browser!")
    except:
        print(f"💡 Manually open: {os.path.abspath(map_file)}")
    
    # Results summary
    print(f"\n📊 BANGALORE ANALYSIS RESULTS:")
    print(f"   Region: Bangalore/South India")
    print(f"   Your planes in region: {len(bangalore_planes)}")
    print(f"   Your drones: {len(drones_df)}")
    print(f"   Collision alerts: {len(alerts)}")
    print(f"   Map file: {map_file}")
    
    if len(alerts) > 0:
        print(f"\n⚠️ COLLISION DETAILS:")
        for i, alert in enumerate(alerts[:5], 1):
            print(f"   {i}. Drone {alert['drone_id']} vs Plane {alert['plane_icao24']}")
            print(f"      Distance: {alert['horizontal_distance']:.2f} km horizontal, "
                  f"{alert['vertical_distance']:.0f} m vertical")
    else:
        print(f"\n✅ No collisions detected - airspace is clear!")
    
    return bangalore_planes, drones_df, alerts

if __name__ == "__main__":
    run_bangalore_analysis()