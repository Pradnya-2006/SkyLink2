"""
SkyLink Fast Collision Detection

Optimized version for processing large datasets with geographic filtering
and spatial indexing for better performance.
"""

import pandas as pd
import numpy as np
from datetime import datetime
from collision_module.collision_detection import detect_collisions
from visualization import plot_airspace
import json
import os


def filter_by_geographic_bounds(df, lat_col='latitude', lon_col='longitude', 
                               bounds=None):
    """
    Filter data by geographic bounds to reduce processing load.
    """
    if bounds is None:
        # Default to New York area
        bounds = {
            'min_lat': 40.0, 'max_lat': 41.5,
            'min_lon': -75.0, 'max_lon': -73.0
        }
    
    filtered = df[
        (df[lat_col] >= bounds['min_lat']) & 
        (df[lat_col] <= bounds['max_lat']) &
        (df[lon_col] >= bounds['min_lon']) & 
        (df[lon_col] <= bounds['max_lon'])
    ]
    
    return filtered


def filter_by_altitude(planes_df, drones_df, max_altitude=1000):
    """
    Filter aircraft by altitude to focus on low-altitude operations.
    """
    # Filter planes (convert to meters if needed)
    low_planes = planes_df[planes_df['baro_altitude'] <= max_altitude]
    
    # Filter drones
    low_drones = drones_df[drones_df['altitude'] <= max_altitude]
    
    return low_planes, low_drones


def sample_data(df, sample_size=100):
    """
    Sample data for faster processing.
    """
    if len(df) <= sample_size:
        return df
    
    return df.sample(n=sample_size, random_state=42)


def main_fast():
    """
    Fast collision detection for large datasets.
    """
    print("Starting SkyLink FAST Collision Detection System...")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Load data
        print("\n1. Loading data...")
        planes_df = pd.read_csv('plane_data/opensky_live_states.csv')
        drones_df = pd.read_csv('drone_data/dummy_drone_dataset_30.csv')
        
        print(f"Original data: {len(planes_df)} planes, {len(drones_df)} drones")
        
        # Step 1: Geographic filtering (focus on specific area)
        print("\n2. Applying geographic filtering...")
        ny_bounds = {
            'min_lat': 40.0, 'max_lat': 41.5,
            'min_lon': -75.0, 'max_lon': -73.0
        }
        
        planes_geo = filter_by_geographic_bounds(planes_df, bounds=ny_bounds)
        drones_geo = filter_by_geographic_bounds(drones_df, bounds=ny_bounds)
        
        print(f"After geographic filter: {len(planes_geo)} planes, {len(drones_geo)} drones")
        
        # Step 2: Altitude filtering (low altitude operations only)
        print("\n3. Applying altitude filtering...")
        planes_filtered, drones_filtered = filter_by_altitude(planes_geo, drones_geo, max_altitude=500)
        
        print(f"After altitude filter: {len(planes_filtered)} planes, {len(drones_filtered)} drones")
        
        # Step 3: Sampling if still too large
        if len(planes_filtered) * len(drones_filtered) > 50000:  # Limit to 50k comparisons
            print("\n4. Applying data sampling for performance...")
            max_planes = min(200, len(planes_filtered))
            max_drones = min(250, len(drones_filtered))
            
            planes_sample = sample_data(planes_filtered, max_planes)
            drones_sample = sample_data(drones_filtered, max_drones)
            
            print(f"After sampling: {len(planes_sample)} planes, {len(drones_sample)} drones")
        else:
            planes_sample = planes_filtered
            drones_sample = drones_filtered
            
        total_comparisons = len(planes_sample) * len(drones_sample)
        print(f"Total comparisons to perform: {total_comparisons:,}")
        
        if total_comparisons == 0:
            print("No aircraft in the filtered area. Expanding search...")
            # Fall back to sampling from original data
            planes_sample = sample_data(planes_df, 50)
            drones_sample = sample_data(drones_df, 100)
            print(f"Using sample: {len(planes_sample)} planes, {len(drones_sample)} drones")
        
        # Step 4: Collision detection
        print(f"\n5. Detecting collisions...")
        start_time = datetime.now()
        
        alerts = detect_collisions(
            planes_sample, 
            drones_sample, 
            h_threshold=0.5,  # 500m horizontal 
            v_threshold=100   # 100m vertical
        )
        
        end_time = datetime.now()
        processing_time = (end_time - start_time).total_seconds()
        
        print(f"Processing completed in {processing_time:.2f} seconds")
        print(f"Found {len(alerts)} collision alerts")
        
        # Step 5: Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save alerts
        if alerts:
            alerts_df = pd.DataFrame(alerts)
            csv_file = f"outputs/fast_collision_alerts_{timestamp}.csv"
            alerts_df.to_csv(csv_file, index=False)
            print(f"Alerts saved to: {csv_file}")
            
            # Save JSON
            json_data = {
                'metadata': {
                    'timestamp': datetime.now().isoformat(),
                    'total_alerts': len(alerts),
                    'processing_time_seconds': processing_time,
                    'planes_processed': len(planes_sample),
                    'drones_processed': len(drones_sample),
                    'filters_applied': ['geographic', 'altitude', 'sampling']
                },
                'alerts': alerts
            }
            
            json_file = f"outputs/fast_collision_alerts_{timestamp}.json"
            with open(json_file, 'w') as f:
                json.dump(json_data, f, indent=2)
            print(f"JSON saved to: {json_file}")
        
        # Step 6: Visualization
        print(f"\n6. Creating visualization...")
        map_file = f"outputs/fast_airspace_map_{timestamp}.html"
        plot_success = plot_airspace(planes_sample, drones_sample, alerts, map_file)
        
        if plot_success:
            print(f"Interactive map saved to: {map_file}")
        
        # Summary
        print(f"\n" + "="*60)
        print("FAST COLLISION DETECTION SUMMARY")
        print("="*60)
        print(f"Original dataset: {len(planes_df):,} planes, {len(drones_df):,} drones")
        print(f"Processed dataset: {len(planes_sample):,} planes, {len(drones_sample):,} drones")
        print(f"Processing time: {processing_time:.2f} seconds")
        print(f"Collision alerts: {len(alerts)}")
        
        if alerts:
            min_h_dist = min(alert['horizontal_distance'] for alert in alerts)
            min_v_dist = min(alert['vertical_distance'] for alert in alerts)
            print(f"Closest encounter: {min_h_dist:.3f} km horizontal, {min_v_dist:.1f} m vertical")
        
        print("="*60)
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main_fast()