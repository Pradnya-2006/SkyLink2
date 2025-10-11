"""
SkyLink Main Application

This is the main entry point for the SkyLink collision detection system.
It orchestrates the entire workflow: data loading, collision detection,
alert saving, and visualization generation.
"""

import pandas as pd
import json
import os
from datetime import datetime
from typing import List, Dict, Optional

# Import our custom modules
from collision_module.collision_detection import detect_collisions, get_collision_summary
from visualization import plot_airspace, create_summary_map


def load_plane_data(file_path: str) -> pd.DataFrame:
    """
    Load plane data from CSV file.
    
    Args:
        file_path (str): Path to the plane data CSV file
    
    Returns:
        pd.DataFrame: DataFrame containing plane data
    """
    try:
        print(f"Loading plane data from: {file_path}")
        
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Plane data file not found: {file_path}")
        
        # Load the CSV file
        planes_df = pd.read_csv(file_path)
        
        # Expected columns for planes
        expected_cols = ['icao24', 'callsign', 'latitude', 'longitude', 'baro_altitude', 'velocity']
        
        # Check if required columns exist
        missing_cols = [col for col in expected_cols if col not in planes_df.columns]
        if missing_cols:
            print(f"Warning: Missing expected columns in plane data: {missing_cols}")
        
        # Clean and validate data
        initial_count = len(planes_df)
        planes_df = planes_df.dropna(subset=['latitude', 'longitude', 'icao24'])
        final_count = len(planes_df)
        
        if initial_count != final_count:
            print(f"Removed {initial_count - final_count} rows with missing critical data")
        
        print(f"Successfully loaded {len(planes_df)} plane records")
        print(f"Plane data columns: {list(planes_df.columns)}")
        
        return planes_df
        
    except Exception as e:
        print(f"Error loading plane data: {e}")
        raise


def load_drone_data(file_path: str) -> pd.DataFrame:
    """
    Load drone data from CSV file.
    
    Args:
        file_path (str): Path to the drone data CSV file
    
    Returns:
        pd.DataFrame: DataFrame containing drone data
    """
    try:
        print(f"Loading drone data from: {file_path}")
        
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Drone data file not found: {file_path}")
        
        # Load the CSV file
        drones_df = pd.read_csv(file_path)
        
        # Expected columns for drones
        expected_cols = ['time_step', 'drone_id', 'latitude', 'longitude', 'altitude', 'speed', 'heading', 'timestamp']
        
        # Check if required columns exist
        missing_cols = [col for col in expected_cols if col not in drones_df.columns]
        if missing_cols:
            print(f"Warning: Missing expected columns in drone data: {missing_cols}")
        
        # Clean and validate data
        initial_count = len(drones_df)
        drones_df = drones_df.dropna(subset=['latitude', 'longitude', 'drone_id'])
        final_count = len(drones_df)
        
        if initial_count != final_count:
            print(f"Removed {initial_count - final_count} rows with missing critical data")
        
        print(f"Successfully loaded {len(drones_df)} drone records")
        print(f"Drone data columns: {list(drones_df.columns)}")
        
        return drones_df
        
    except Exception as e:
        print(f"Error loading drone data: {e}")
        raise


def save_alerts_to_json(alerts: List[Dict], file_path: str) -> bool:
    """
    Save collision alerts to JSON file.
    
    Args:
        alerts (List[Dict]): List of collision alerts
        file_path (str): Output file path for JSON
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Create output directory if it doesn't exist
        output_dir = os.path.dirname(file_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # Prepare data for JSON serialization
        json_data = {
            'metadata': {
                'timestamp': datetime.now().isoformat(),
                'total_alerts': len(alerts),
                'system': 'SkyLink Collision Detection System'
            },
            'alerts': alerts
        }
        
        # Save to JSON file
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=2, ensure_ascii=False)
        
        print(f"Alerts saved to JSON: {file_path}")
        return True
        
    except Exception as e:
        print(f"Error saving alerts to JSON: {e}")
        return False


def save_alerts_to_csv(alerts: List[Dict], file_path: str) -> bool:
    """
    Save collision alerts to CSV file.
    
    Args:
        alerts (List[Dict]): List of collision alerts
        file_path (str): Output file path for CSV
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        if not alerts:
            print("No alerts to save to CSV")
            return True
        
        # Create output directory if it doesn't exist
        output_dir = os.path.dirname(file_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # Convert alerts to DataFrame and save
        alerts_df = pd.DataFrame(alerts)
        alerts_df.to_csv(file_path, index=False)
        
        print(f"Alerts saved to CSV: {file_path}")
        return True
        
    except Exception as e:
        print(f"Error saving alerts to CSV: {e}")
        return False


def print_summary(planes_df: pd.DataFrame, drones_df: pd.DataFrame, alerts: List[Dict]) -> None:
    """
    Print a summary of the collision detection results.
    
    Args:
        planes_df (pd.DataFrame): DataFrame containing plane data
        drones_df (pd.DataFrame): DataFrame containing drone data
        alerts (List[Dict]): List of collision alerts
    """
    print("\n" + "="*60)
    print("SKYLINK COLLISION DETECTION SUMMARY")
    print("="*60)
    
    # Basic statistics
    print(f"Planes loaded: {len(planes_df)}")
    print(f"Drones loaded: {len(drones_df)}")
    print(f"Total alerts generated: {len(alerts)}")
    
    # Get detailed summary
    summary = get_collision_summary(alerts)
    
    if alerts:
        print(f"\nAlert Details:")
        print(f"  - Unique drones involved: {summary['unique_drones']}")
        print(f"  - Unique planes involved: {summary['unique_planes']}")
        print(f"  - Average horizontal distance: {summary['avg_horizontal_distance']} km")
        print(f"  - Average vertical distance: {summary['avg_vertical_distance']} m")
        print(f"  - Minimum horizontal distance: {summary['min_horizontal_distance']} km")
        print(f"  - Minimum vertical distance: {summary['min_vertical_distance']} m")
        
        # Show top 5 closest encounters
        if len(alerts) > 0:
            print(f"\nTop 5 Closest Encounters:")
            sorted_alerts = sorted(alerts, key=lambda x: x['horizontal_distance'])[:5]
            for i, alert in enumerate(sorted_alerts, 1):
                print(f"  {i}. Drone {alert['drone_id']} vs Plane {alert['plane_icao24']}: "
                      f"{alert['horizontal_distance']} km, {alert['vertical_distance']} m")
    else:
        print("\nNo collision alerts detected - airspace is clear!")
    
    print("="*60)


def main():
    """
    Main function to run the SkyLink collision detection system.
    """
    print("Starting SkyLink Collision Detection System...")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Define file paths
        plane_data_path = "plane_data/opensky_live_states.csv"
        drone_data_path = "drone_data/dummy_drone_dataset_30.csv"
        
        # Load data
        print("\n1. Loading data...")
        planes_df = load_plane_data(plane_data_path)
        drones_df = load_drone_data(drone_data_path)
        
        # Configure collision detection thresholds
        horizontal_threshold = 0.5  # kilometers
        vertical_threshold = 100   # meters
        
        print(f"\n2. Detecting collisions...")
        print(f"   Horizontal threshold: {horizontal_threshold} km")
        print(f"   Vertical threshold: {vertical_threshold} m")
        
        # Detect collisions
        alerts = detect_collisions(
            planes_df, 
            drones_df, 
            h_threshold=horizontal_threshold, 
            v_threshold=vertical_threshold
        )
        
        # Save alerts
        print(f"\n3. Saving alerts...")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save to JSON
        json_file = f"outputs/collision_alerts_{timestamp}.json"
        save_alerts_to_json(alerts, json_file)
        
        # Save to CSV
        csv_file = f"outputs/collision_alerts_{timestamp}.csv"
        save_alerts_to_csv(alerts, csv_file)
        
        # Create visualizations
        print(f"\n4. Creating visualizations...")
        
        # Main airspace map
        map_file = f"outputs/airspace_map_{timestamp}.html"
        plot_success = plot_airspace(planes_df, drones_df, alerts, map_file)
        
        # Summary map (if there are alerts)
        if alerts:
            summary_map_file = f"outputs/alerts_summary_{timestamp}.html"
            create_summary_map(alerts, summary_map_file)
        
        # Print summary
        print_summary(planes_df, drones_df, alerts)
        
        # Final status
        print(f"\nSystem execution completed successfully!")
        print(f"Check the 'outputs/' folder for results:")
        print(f"  - Alerts JSON: {json_file}")
        print(f"  - Alerts CSV: {csv_file}")
        print(f"  - Airspace Map: {map_file}")
        if alerts:
            print(f"  - Summary Map: {summary_map_file}")
        
    except FileNotFoundError as e:
        print(f"\nERROR: Required data file not found: {e}")
        print("Please ensure both CSV files are in their respective directories:")
        print("  - plane_data/opensky_live_states.csv")
        print("  - drone_data/dummy_drone_dataset_30.csv")
        
    except Exception as e:
        print(f"\nERROR: An unexpected error occurred: {e}")
        print("Please check your data files and try again.")


if __name__ == "__main__":
    main()