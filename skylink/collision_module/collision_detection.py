"""
SkyLink Collision Detection Module

This module provides collision detection functionality between drones and planes
using configurable horizontal and vertical distance thresholds.
"""

import numpy as np
import pandas as pd
from geopy.distance import geodesic
from typing import List, Dict, Tuple


def calculate_horizontal_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the horizontal distance between two geographic points using the geodesic formula.
    
    Args:
        lat1 (float): Latitude of first point
        lon1 (float): Longitude of first point
        lat2 (float): Latitude of second point
        lon2 (float): Longitude of second point
    
    Returns:
        float: Distance in kilometers
    """
    try:
        point1 = (lat1, lon1)
        point2 = (lat2, lon2)
        distance = geodesic(point1, point2).kilometers
        return distance
    except Exception as e:
        print(f"Error calculating distance: {e}")
        return float('inf')


def calculate_vertical_distance(altitude1: float, altitude2: float) -> float:
    """
    Calculate the vertical distance between two altitudes.
    
    Args:
        altitude1 (float): First altitude in meters
        altitude2 (float): Second altitude in meters
    
    Returns:
        float: Vertical distance in meters
    """
    return abs(altitude1 - altitude2)


def detect_collisions(planes_df: pd.DataFrame, drones_df: pd.DataFrame, 
                     h_threshold: float = 0.5, v_threshold: float = 100) -> List[Dict]:
    """
    Detect potential collisions between drones and planes based on distance thresholds.
    
    Args:
        planes_df (pd.DataFrame): DataFrame containing plane data with columns:
                                 ['icao24', 'callsign', 'latitude', 'longitude', 'baro_altitude', 'velocity']
        drones_df (pd.DataFrame): DataFrame containing drone data with columns:
                                 ['time_step', 'drone_id', 'latitude', 'longitude', 'altitude', 'speed', 'heading', 'timestamp']
        h_threshold (float): Horizontal distance threshold in kilometers (default: 0.5)
        v_threshold (float): Vertical distance threshold in meters (default: 100)
    
    Returns:
        List[Dict]: List of collision alerts, each containing:
                   - drone_id: ID of the drone
                   - plane_icao24: ICAO24 code of the plane
                   - horizontal_distance: Horizontal distance in km
                   - vertical_distance: Vertical distance in meters
                   - drone_lat: Drone latitude
                   - drone_lon: Drone longitude
                   - plane_lat: Plane latitude
                   - plane_lon: Plane longitude
                   - drone_altitude: Drone altitude in meters
                   - plane_altitude: Plane altitude in meters
    """
    alerts = []
    
    # Validate input data
    if planes_df.empty or drones_df.empty:
        print("Warning: One or both datasets are empty")
        return alerts
    
    # Required columns for planes
    required_plane_cols = ['icao24', 'latitude', 'longitude', 'baro_altitude']
    missing_plane_cols = [col for col in required_plane_cols if col not in planes_df.columns]
    if missing_plane_cols:
        raise ValueError(f"Missing required plane columns: {missing_plane_cols}")
    
    # Required columns for drones
    required_drone_cols = ['drone_id', 'latitude', 'longitude', 'altitude']
    missing_drone_cols = [col for col in required_drone_cols if col not in drones_df.columns]
    if missing_drone_cols:
        raise ValueError(f"Missing required drone columns: {missing_drone_cols}")
    
    # Filter out rows with missing critical data
    planes_clean = planes_df.dropna(subset=['icao24', 'latitude', 'longitude', 'baro_altitude'])
    drones_clean = drones_df.dropna(subset=['drone_id', 'latitude', 'longitude', 'altitude'])
    
    print(f"Processing {len(planes_clean)} planes and {len(drones_clean)} drones for collision detection...")
    
    # Iterate through all plane-drone pairs
    collision_count = 0
    total_pairs = len(planes_clean) * len(drones_clean)
    
    for plane_idx, plane in planes_clean.iterrows():
        for drone_idx, drone in drones_clean.iterrows():
            try:
                # Calculate horizontal distance
                h_distance = calculate_horizontal_distance(
                    plane['latitude'], plane['longitude'],
                    drone['latitude'], drone['longitude']
                )
                
                # Calculate vertical distance (convert plane altitude to meters if needed)
                plane_altitude_m = float(plane['baro_altitude'])  # Assuming already in meters
                drone_altitude_m = float(drone['altitude'])
                v_distance = calculate_vertical_distance(plane_altitude_m, drone_altitude_m)
                
                # Check if thresholds are exceeded
                if h_distance <= h_threshold and v_distance <= v_threshold:
                    alert = {
                        'drone_id': drone['drone_id'],
                        'plane_icao24': plane['icao24'],
                        'horizontal_distance': round(h_distance, 3),
                        'vertical_distance': round(v_distance, 2),
                        'drone_lat': drone['latitude'],
                        'drone_lon': drone['longitude'],
                        'plane_lat': plane['latitude'],
                        'plane_lon': plane['longitude'],
                        'drone_altitude': drone_altitude_m,
                        'plane_altitude': plane_altitude_m,
                        'callsign': plane.get('callsign', 'N/A'),
                        'drone_speed': drone.get('speed', 'N/A'),
                        'plane_velocity': plane.get('velocity', 'N/A')
                    }
                    alerts.append(alert)
                    collision_count += 1
                    
            except Exception as e:
                print(f"Error processing pair - Plane: {plane.get('icao24', 'Unknown')}, "
                      f"Drone: {drone.get('drone_id', 'Unknown')}: {e}")
                continue
    
    print(f"Collision detection complete: {collision_count} potential collisions detected "
          f"out of {total_pairs} plane-drone pairs")
    
    return alerts


def get_collision_summary(alerts: List[Dict]) -> Dict:
    """
    Generate a summary of collision detection results.
    
    Args:
        alerts (List[Dict]): List of collision alerts
    
    Returns:
        Dict: Summary statistics
    """
    if not alerts:
        return {
            'total_alerts': 0,
            'unique_drones': 0,
            'unique_planes': 0,
            'avg_horizontal_distance': 0,
            'avg_vertical_distance': 0,
            'min_horizontal_distance': 0,
            'min_vertical_distance': 0
        }
    
    alerts_df = pd.DataFrame(alerts)
    
    return {
        'total_alerts': len(alerts),
        'unique_drones': alerts_df['drone_id'].nunique(),
        'unique_planes': alerts_df['plane_icao24'].nunique(),
        'avg_horizontal_distance': round(alerts_df['horizontal_distance'].mean(), 3),
        'avg_vertical_distance': round(alerts_df['vertical_distance'].mean(), 2),
        'min_horizontal_distance': round(alerts_df['horizontal_distance'].min(), 3),
        'min_vertical_distance': round(alerts_df['vertical_distance'].min(), 2)
    }