"""
SkyLink Regional Analysis Tool

This tool provides focused collision detection for specific geographic regions
and altitude ranges, making it suitable for real-world applications.
"""

import pandas as pd
import numpy as np
from datetime import datetime
from collision_module.collision_detection import detect_collisions
from visualization import plot_airspace
import json
import os


# Predefined regions of interest
REGIONS = {
    'new_york': {
        'name': 'New York Metropolitan Area',
        'bounds': {'min_lat': 40.4, 'max_lat': 41.0, 'min_lon': -74.5, 'max_lon': -73.5}
    },
    'los_angeles': {
        'name': 'Los Angeles Area',
        'bounds': {'min_lat': 33.7, 'max_lat': 34.3, 'min_lon': -118.7, 'max_lon': -117.9}
    },
    'chicago': {
        'name': 'Chicago Area',
        'bounds': {'min_lat': 41.6, 'max_lat': 42.1, 'min_lon': -88.0, 'max_lon': -87.3}
    },
    'miami': {
        'name': 'Miami Area',
        'bounds': {'min_lat': 25.6, 'max_lat': 26.0, 'min_lon': -80.5, 'max_lon': -80.1}
    },
    'custom': {
        'name': 'Custom Region',
        'bounds': {'min_lat': 40.0, 'max_lat': 41.0, 'min_lon': -75.0, 'max_lon': -73.0}
    }
}


def analyze_region(region_key='new_york', altitude_limit=1000, 
                  h_threshold=0.5, v_threshold=100, max_samples=None):
    """
    Analyze collision risk in a specific region.
    
    Args:
        region_key: Key for predefined region or 'custom'
        altitude_limit: Maximum altitude to analyze (meters)
        h_threshold: Horizontal distance threshold (km)
        v_threshold: Vertical distance threshold (meters)
        max_samples: Maximum number of aircraft to sample (None for no limit)
    """
    print(f"Analyzing region: {REGIONS[region_key]['name']}")
    print("="*60)
    
    # Load data
    planes_df = pd.read_csv('plane_data/opensky_live_states.csv')
    drones_df = pd.read_csv('drone_data/dummy_drone_dataset_30.csv')
    
    print(f"Total dataset: {len(planes_df):,} planes, {len(drones_df):,} drones")
    
    # Filter by region
    bounds = REGIONS[region_key]['bounds']
    
    # Filter planes
    regional_planes = planes_df[
        (planes_df['latitude'] >= bounds['min_lat']) &
        (planes_df['latitude'] <= bounds['max_lat']) &
        (planes_df['longitude'] >= bounds['min_lon']) &
        (planes_df['longitude'] <= bounds['max_lon']) &
        (planes_df['baro_altitude'] <= altitude_limit)
    ].copy()
    
    # Filter drones
    regional_drones = drones_df[
        (drones_df['latitude'] >= bounds['min_lat']) &
        (drones_df['latitude'] <= bounds['max_lat']) &
        (drones_df['longitude'] >= bounds['min_lon']) &
        (drones_df['longitude'] <= bounds['max_lon']) &
        (drones_df['altitude'] <= altitude_limit)
    ].copy()
    
    print(f"Regional dataset: {len(regional_planes):,} planes, {len(regional_drones):,} drones")
    print(f"Altitude limit: {altitude_limit} meters")
    
    # Sample if necessary
    if max_samples and len(regional_planes) > max_samples:
        regional_planes = regional_planes.sample(n=max_samples, random_state=42)
        print(f"Sampled planes to {len(regional_planes):,}")
    
    if max_samples and len(regional_drones) > max_samples:
        regional_drones = regional_drones.sample(n=max_samples, random_state=42)
        print(f"Sampled drones to {len(regional_drones):,}")
    
    # Fall back to global sampling if regional data is insufficient
    if len(regional_planes) == 0 or len(regional_drones) == 0:
        print("Insufficient regional data. Using global sampling...")
        regional_planes = planes_df[planes_df['baro_altitude'] <= altitude_limit].sample(
            n=min(50, len(planes_df)), random_state=42
        )
        regional_drones = drones_df[drones_df['altitude'] <= altitude_limit].sample(
            n=min(100, len(drones_df)), random_state=42
        )
        print(f"Global sample: {len(regional_planes)} planes, {len(regional_drones)} drones")
    
    # Collision detection
    print(f"\nRunning collision detection...")
    print(f"Thresholds: {h_threshold} km horizontal, {v_threshold} m vertical")
    
    start_time = datetime.now()
    alerts = detect_collisions(
        regional_planes, 
        regional_drones, 
        h_threshold=h_threshold,
        v_threshold=v_threshold
    )
    end_time = datetime.now()
    
    processing_time = (end_time - start_time).total_seconds()
    
    # Create visualization
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    map_file = f"outputs/regional_{region_key}_{timestamp}.html"
    plot_airspace(regional_planes, regional_drones, alerts, map_file)
    
    # Save detailed results
    results = {
        'region': REGIONS[region_key]['name'],
        'analysis_time': datetime.now().isoformat(),
        'processing_time_seconds': processing_time,
        'parameters': {
            'altitude_limit_m': altitude_limit,
            'horizontal_threshold_km': h_threshold,
            'vertical_threshold_m': v_threshold
        },
        'aircraft_counts': {
            'total_planes': len(planes_df),
            'total_drones': len(drones_df),
            'regional_planes': len(regional_planes),
            'regional_drones': len(regional_drones)
        },
        'alerts': {
            'total_count': len(alerts),
            'alerts_data': alerts
        }
    }
    
    # Save results
    results_file = f"outputs/regional_analysis_{region_key}_{timestamp}.json"
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    if alerts:
        alerts_df = pd.DataFrame(alerts)
        csv_file = f"outputs/regional_alerts_{region_key}_{timestamp}.csv"
        alerts_df.to_csv(csv_file, index=False)
    
    # Print summary
    print(f"\nREGIONAL ANALYSIS RESULTS")
    print("="*60)
    print(f"Region: {REGIONS[region_key]['name']}")
    print(f"Aircraft processed: {len(regional_planes)} planes, {len(regional_drones)} drones")
    print(f"Processing time: {processing_time:.2f} seconds")
    print(f"Collision alerts: {len(alerts)}")
    
    if alerts:
        min_h_dist = min(alert['horizontal_distance'] for alert in alerts)
        min_v_dist = min(alert['vertical_distance'] for alert in alerts)
        print(f"Closest encounter: {min_h_dist:.3f} km horizontal, {min_v_dist:.1f} m vertical")
        
        # Risk assessment
        high_risk = [a for a in alerts if a['horizontal_distance'] < 0.2]
        medium_risk = [a for a in alerts if 0.2 <= a['horizontal_distance'] < 0.4]
        
        print(f"Risk levels:")
        print(f"  High risk alerts (< 0.2 km): {len(high_risk)}")
        print(f"  Medium risk alerts (0.2-0.4 km): {len(medium_risk)}")
        print(f"  Low risk alerts (> 0.4 km): {len(alerts) - len(high_risk) - len(medium_risk)}")
    
    print(f"\nOutput files:")
    print(f"  Map: {map_file}")
    print(f"  Analysis: {results_file}")
    if alerts:
        print(f"  Alerts CSV: {csv_file}")
    
    return results


def interactive_analysis():
    """
    Interactive regional analysis with user input.
    """
    print("SkyLink Regional Collision Analysis Tool")
    print("="*50)
    
    # Show available regions
    print("\nAvailable regions:")
    for key, region in REGIONS.items():
        if key != 'custom':
            print(f"  {key}: {region['name']}")
    
    # Get user choices (with defaults for automation)
    region_choice = 'new_york'  # Default choice
    altitude_limit = 1000      # Default altitude
    h_threshold = 0.5         # Default horizontal threshold
    v_threshold = 100         # Default vertical threshold
    
    print(f"\nUsing defaults:")
    print(f"Region: {region_choice}")
    print(f"Altitude limit: {altitude_limit} m")
    print(f"Horizontal threshold: {h_threshold} km")
    print(f"Vertical threshold: {v_threshold} m")
    
    # Run analysis
    results = analyze_region(
        region_key=region_choice,
        altitude_limit=altitude_limit,
        h_threshold=h_threshold,
        v_threshold=v_threshold,
        max_samples=200  # Limit for performance
    )
    
    return results


def multi_region_analysis():
    """
    Analyze multiple regions and compare results.
    """
    print("Multi-Region Collision Analysis")
    print("="*50)
    
    regions_to_analyze = ['new_york', 'los_angeles', 'chicago']
    all_results = {}
    
    for region in regions_to_analyze:
        print(f"\n\nAnalyzing {region}...")
        results = analyze_region(
            region_key=region,
            altitude_limit=800,
            max_samples=100
        )
        all_results[region] = results
    
    # Comparison summary
    print(f"\n\nMULTI-REGION COMPARISON")
    print("="*60)
    
    for region, results in all_results.items():
        alert_count = results['alerts']['total_count']
        aircraft_count = results['aircraft_counts']['regional_planes'] + results['aircraft_counts']['regional_drones']
        print(f"{REGIONS[region]['name']:30} | {alert_count:3} alerts | {aircraft_count:3} aircraft")
    
    return all_results


if __name__ == "__main__":
    # Run interactive analysis
    interactive_analysis()