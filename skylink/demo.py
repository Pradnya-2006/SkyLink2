"""
SkyLink Demonstration Script

This script demonstrates how to use the SkyLink system programmatically
with custom parameters and configurations.
"""

import pandas as pd
from collision_module.collision_detection import detect_collisions, get_collision_summary
from visualization import plot_airspace, create_summary_map


def demo_custom_thresholds():
    """
    Demonstrate collision detection with custom thresholds.
    """
    print("=" * 60)
    print("SKYLINK CUSTOM THRESHOLD DEMONSTRATION")
    print("=" * 60)
    
    # Load data
    planes_df = pd.read_csv('plane_data/opensky_live_states.csv')
    drones_df = pd.read_csv('drone_data/dummy_drone_dataset_30.csv')
    
    print(f"Loaded {len(planes_df)} planes and {len(drones_df)} drones\n")
    
    # Test different threshold configurations
    test_configs = [
        {"h_threshold": 0.1, "v_threshold": 50, "name": "Very Strict"},
        {"h_threshold": 0.3, "v_threshold": 75, "name": "Strict"},
        {"h_threshold": 0.5, "v_threshold": 100, "name": "Standard"},
        {"h_threshold": 1.0, "v_threshold": 200, "name": "Relaxed"}
    ]
    
    for config in test_configs:
        print(f"\n{config['name']} Configuration:")
        print(f"  Horizontal threshold: {config['h_threshold']} km")
        print(f"  Vertical threshold: {config['v_threshold']} m")
        
        alerts = detect_collisions(
            planes_df, 
            drones_df, 
            h_threshold=config['h_threshold'],
            v_threshold=config['v_threshold']
        )
        
        summary = get_collision_summary(alerts)
        print(f"  Alerts generated: {summary['total_alerts']}")
        
        if alerts:
            print(f"  Min horizontal distance: {summary['min_horizontal_distance']} km")
            print(f"  Min vertical distance: {summary['min_vertical_distance']} m")
        
        # Create visualization for each configuration
        map_file = f"outputs/demo_{config['name'].lower().replace(' ', '_')}_map.html"
        plot_airspace(planes_df, drones_df, alerts, map_file)
        print(f"  Map saved: {map_file}")


def demo_data_filtering():
    """
    Demonstrate filtering data before collision detection.
    """
    print("\n" + "=" * 60)
    print("SKYLINK DATA FILTERING DEMONSTRATION")
    print("=" * 60)
    
    # Load data
    planes_df = pd.read_csv('plane_data/opensky_live_states.csv')
    drones_df = pd.read_csv('drone_data/dummy_drone_dataset_30.csv')
    
    # Filter by altitude - only check aircraft below 300m
    low_altitude_planes = planes_df[planes_df['baro_altitude'] <= 300]
    low_altitude_drones = drones_df[drones_df['altitude'] <= 300]
    
    print(f"Original data: {len(planes_df)} planes, {len(drones_df)} drones")
    print(f"Low altitude filter: {len(low_altitude_planes)} planes, {len(low_altitude_drones)} drones")
    
    # Detect collisions in low altitude airspace
    alerts = detect_collisions(low_altitude_planes, low_altitude_drones)
    
    summary = get_collision_summary(alerts)
    print(f"Low altitude alerts: {summary['total_alerts']}")
    
    # Create visualization
    plot_airspace(
        low_altitude_planes, 
        low_altitude_drones, 
        alerts, 
        "outputs/demo_low_altitude_map.html"
    )
    print("Low altitude map saved: outputs/demo_low_altitude_map.html")


def demo_real_time_simulation():
    """
    Demonstrate processing data in time steps (simulating real-time).
    """
    print("\n" + "=" * 60)
    print("SKYLINK TIME-STEP SIMULATION DEMONSTRATION")
    print("=" * 60)
    
    # Load data
    planes_df = pd.read_csv('plane_data/opensky_live_states.csv')
    drones_df = pd.read_csv('drone_data/dummy_drone_dataset_30.csv')
    
    # Process each time step separately
    time_steps = drones_df['time_step'].unique()
    
    all_time_alerts = []
    
    for step in sorted(time_steps):
        step_drones = drones_df[drones_df['time_step'] == step]
        
        print(f"\nTime step {step}:")
        print(f"  Processing {len(step_drones)} drones vs {len(planes_df)} planes")
        
        alerts = detect_collisions(planes_df, step_drones)
        all_time_alerts.extend(alerts)
        
        print(f"  Alerts in this time step: {len(alerts)}")
        
        # Create map for this time step
        if alerts:
            map_file = f"outputs/demo_timestep_{step}_map.html"
            plot_airspace(planes_df, step_drones, alerts, map_file)
            print(f"  Time step map saved: {map_file}")
    
    print(f"\nTotal alerts across all time steps: {len(all_time_alerts)}")


def main():
    """
    Run all demonstration functions.
    """
    try:
        demo_custom_thresholds()
        demo_data_filtering() 
        demo_real_time_simulation()
        
        print("\n" + "=" * 60)
        print("ALL DEMONSTRATIONS COMPLETED SUCCESSFULLY!")
        print("Check the 'outputs/' folder for generated maps and data.")
        print("=" * 60)
        
    except Exception as e:
        print(f"Error during demonstration: {e}")


if __name__ == "__main__":
    main()