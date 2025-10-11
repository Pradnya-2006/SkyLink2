"""
SkyLink Visualization Module

This module provides visualization functionality for displaying planes, drones,
and collision alerts on interactive maps using Folium.
"""

import folium
import pandas as pd
from typing import List, Dict, Tuple, Optional
import os


def calculate_map_center(planes_df: pd.DataFrame, drones_df: pd.DataFrame) -> Tuple[float, float]:
    """
    Calculate the center point for the map based on plane and drone positions.
    
    Args:
        planes_df (pd.DataFrame): DataFrame containing plane data
        drones_df (pd.DataFrame): DataFrame containing drone data
    
    Returns:
        Tuple[float, float]: Latitude and longitude of map center
    """
    all_lats = []
    all_lons = []
    
    # Collect all valid coordinates
    if not planes_df.empty:
        plane_lats = planes_df['latitude'].dropna().tolist()
        plane_lons = planes_df['longitude'].dropna().tolist()
        all_lats.extend(plane_lats)
        all_lons.extend(plane_lons)
    
    if not drones_df.empty:
        drone_lats = drones_df['latitude'].dropna().tolist()
        drone_lons = drones_df['longitude'].dropna().tolist()
        all_lats.extend(drone_lats)
        all_lons.extend(drone_lons)
    
    if all_lats and all_lons:
        center_lat = sum(all_lats) / len(all_lats)
        center_lon = sum(all_lons) / len(all_lons)
        return center_lat, center_lon
    else:
        # Default center (roughly middle of US)
        return 39.8283, -98.5795


def add_planes_to_map(map_obj: folium.Map, planes_df: pd.DataFrame) -> int:
    """
    Add plane markers to the folium map.
    
    Args:
        map_obj (folium.Map): Folium map object
        planes_df (pd.DataFrame): DataFrame containing plane data
    
    Returns:
        int: Number of planes added to the map
    """
    planes_added = 0
    
    for idx, plane in planes_df.iterrows():
        try:
            # Skip rows with missing coordinates
            if pd.isna(plane['latitude']) or pd.isna(plane['longitude']):
                continue
            
            # Create popup text with plane information
            popup_text = f"""
            <b>Aircraft</b><br>
            ICAO24: {plane.get('icao24', 'N/A')}<br>
            Callsign: {plane.get('callsign', 'N/A')}<br>
            Altitude: {plane.get('baro_altitude', 'N/A')} m<br>
            Velocity: {plane.get('velocity', 'N/A')} m/s<br>
            Lat: {plane['latitude']:.4f}<br>
            Lon: {plane['longitude']:.4f}
            """
            
            # Add plane marker (blue circle)
            folium.CircleMarker(
                location=[plane['latitude'], plane['longitude']],
                radius=8,
                popup=folium.Popup(popup_text, max_width=200),
                color='blue',
                fill=True,
                fillColor='lightblue',
                fillOpacity=0.7,
                weight=2,
                tooltip=f"Plane: {plane.get('callsign', plane.get('icao24', 'Unknown'))}"
            ).add_to(map_obj)
            
            planes_added += 1
            
        except Exception as e:
            print(f"Error adding plane {plane.get('icao24', 'Unknown')}: {e}")
            continue
    
    return planes_added


def add_drones_to_map(map_obj: folium.Map, drones_df: pd.DataFrame) -> int:
    """
    Add drone markers to the folium map.
    
    Args:
        map_obj (folium.Map): Folium map object
        drones_df (pd.DataFrame): DataFrame containing drone data
    
    Returns:
        int: Number of drones added to the map
    """
    drones_added = 0
    
    for idx, drone in drones_df.iterrows():
        try:
            # Skip rows with missing coordinates
            if pd.isna(drone['latitude']) or pd.isna(drone['longitude']):
                continue
            
            # Create popup text with drone information
            popup_text = f"""
            <b>Drone</b><br>
            ID: {drone.get('drone_id', 'N/A')}<br>
            Altitude: {drone.get('altitude', 'N/A')} m<br>
            Speed: {drone.get('speed', 'N/A')} m/s<br>
            Heading: {drone.get('heading', 'N/A')}°<br>
            Lat: {drone['latitude']:.4f}<br>
            Lon: {drone['longitude']:.4f}<br>
            Time: {drone.get('timestamp', 'N/A')}
            """
            
            # Add drone marker (green circle)
            folium.CircleMarker(
                location=[drone['latitude'], drone['longitude']],
                radius=6,
                popup=folium.Popup(popup_text, max_width=200),
                color='green',
                fill=True,
                fillColor='lightgreen',
                fillOpacity=0.7,
                weight=2,
                tooltip=f"Drone: {drone.get('drone_id', 'Unknown')}"
            ).add_to(map_obj)
            
            drones_added += 1
            
        except Exception as e:
            print(f"Error adding drone {drone.get('drone_id', 'Unknown')}: {e}")
            continue
    
    return drones_added


def add_alerts_to_map(map_obj: folium.Map, alerts: List[Dict]) -> int:
    """
    Add collision alert markers to the folium map.
    
    Args:
        map_obj (folium.Map): Folium map object
        alerts (List[Dict]): List of collision alerts
    
    Returns:
        int: Number of alerts added to the map
    """
    alerts_added = 0
    
    for alert in alerts:
        try:
            # Calculate midpoint between drone and plane for alert marker
            alert_lat = (alert['drone_lat'] + alert['plane_lat']) / 2
            alert_lon = (alert['drone_lon'] + alert['plane_lon']) / 2
            
            # Create popup text with alert information
            popup_text = f"""
            <b>COLLISION ALERT</b><br>
            Drone ID: {alert.get('drone_id', 'N/A')}<br>
            Plane ICAO24: {alert.get('plane_icao24', 'N/A')}<br>
            Horizontal Distance: {alert.get('horizontal_distance', 'N/A')} km<br>
            Vertical Distance: {alert.get('vertical_distance', 'N/A')} m<br>
            Drone Alt: {alert.get('drone_altitude', 'N/A')} m<br>
            Plane Alt: {alert.get('plane_altitude', 'N/A')} m
            """
            
            # Add alert marker (red circle with warning icon)
            folium.CircleMarker(
                location=[alert_lat, alert_lon],
                radius=12,
                popup=folium.Popup(popup_text, max_width=250),
                color='red',
                fill=True,
                fillColor='red',
                fillOpacity=0.8,
                weight=3,
                tooltip=f"ALERT: Drone {alert.get('drone_id')} vs Plane {alert.get('plane_icao24')}"
            ).add_to(map_obj)
            
            # Add connecting lines between drone and plane
            folium.PolyLine(
                locations=[
                    [alert['drone_lat'], alert['drone_lon']],
                    [alert['plane_lat'], alert['plane_lon']]
                ],
                color='red',
                weight=2,
                opacity=0.6,
                dash_array='5, 10'
            ).add_to(map_obj)
            
            alerts_added += 1
            
        except Exception as e:
            print(f"Error adding alert for drone {alert.get('drone_id', 'Unknown')}: {e}")
            continue
    
    return alerts_added


def plot_airspace(planes_df: pd.DataFrame, drones_df: pd.DataFrame, alerts: List[Dict], 
                  map_file: str = "outputs/airspace_map.html") -> bool:
    """
    Create an interactive folium map showing planes, drones, and collision alerts.
    
    Args:
        planes_df (pd.DataFrame): DataFrame containing plane data
        drones_df (pd.DataFrame): DataFrame containing drone data
        alerts (List[Dict]): List of collision alerts
        map_file (str): Output file path for the HTML map (default: "outputs/airspace_map.html")
    
    Returns:
        bool: True if map was successfully created and saved, False otherwise
    """
    try:
        # Calculate map center
        center_lat, center_lon = calculate_map_center(planes_df, drones_df)
        
        # Create base map
        airspace_map = folium.Map(
            location=[center_lat, center_lon],
            zoom_start=8,
            tiles='OpenStreetMap'
        )
        
        # Add alternative tile layers
        folium.TileLayer('CartoDB positron').add_to(airspace_map)
        
        # Add layer control
        folium.LayerControl().add_to(airspace_map)
        
        # Add planes to map
        planes_count = add_planes_to_map(airspace_map, planes_df)
        print(f"Added {planes_count} planes to the map")
        
        # Add drones to map
        drones_count = add_drones_to_map(airspace_map, drones_df)
        print(f"Added {drones_count} drones to the map")
        
        # Add alerts to map
        alerts_count = add_alerts_to_map(airspace_map, alerts)
        print(f"Added {alerts_count} collision alerts to the map")
        
        # Add legend
        legend_html = '''
        <div style="position: fixed; 
                    bottom: 50px; left: 50px; width: 150px; height: 120px; 
                    background-color: white; border:2px solid grey; z-index:9999; 
                    font-size:14px; padding: 10px">
        <p><b>Legend</b></p>
        <p><i class="fa fa-circle" style="color:lightblue"></i> Planes ({planes_count})</p>
        <p><i class="fa fa-circle" style="color:lightgreen"></i> Drones ({drones_count})</p>
        <p><i class="fa fa-circle" style="color:red"></i> Alerts ({alerts_count})</p>
        </div>
        '''.format(planes_count=planes_count, drones_count=drones_count, alerts_count=alerts_count)
        
        airspace_map.get_root().html.add_child(folium.Element(legend_html))
        
        # Create output directory if it doesn't exist
        output_dir = os.path.dirname(map_file)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # Save the map
        airspace_map.save(map_file)
        print(f"Airspace map saved to: {map_file}")
        
        return True
        
    except Exception as e:
        print(f"Error creating airspace map: {e}")
        return False


def create_summary_map(alerts: List[Dict], map_file: str = "outputs/alerts_summary_map.html") -> bool:
    """
    Create a summary map showing only collision alerts with enhanced details.
    
    Args:
        alerts (List[Dict]): List of collision alerts
        map_file (str): Output file path for the HTML map
    
    Returns:
        bool: True if map was successfully created and saved, False otherwise
    """
    try:
        if not alerts:
            print("No alerts to display on summary map")
            return False
        
        # Calculate center from alerts
        alert_lats = [(alert['drone_lat'] + alert['plane_lat']) / 2 for alert in alerts]
        alert_lons = [(alert['drone_lon'] + alert['plane_lon']) / 2 for alert in alerts]
        
        center_lat = sum(alert_lats) / len(alert_lats)
        center_lon = sum(alert_lons) / len(alert_lons)
        
        # Create map
        summary_map = folium.Map(
            location=[center_lat, center_lon],
            zoom_start=10,
            tiles='OpenStreetMap'
        )
        
        # Add alerts with enhanced information
        for i, alert in enumerate(alerts, 1):
            alert_lat = (alert['drone_lat'] + alert['plane_lat']) / 2
            alert_lon = (alert['drone_lon'] + alert['plane_lon']) / 2
            
            popup_text = f"""
            <b>Alert #{i}</b><br>
            <b>Risk Level:</b> {'HIGH' if alert['horizontal_distance'] < 0.2 else 'MEDIUM'}<br>
            Drone: {alert.get('drone_id', 'N/A')}<br>
            Plane: {alert.get('plane_icao24', 'N/A')}<br>
            H-Distance: {alert.get('horizontal_distance', 'N/A')} km<br>
            V-Distance: {alert.get('vertical_distance', 'N/A')} m<br>
            """
            
            # Color based on risk level
            color = 'darkred' if alert['horizontal_distance'] < 0.2 else 'orange'
            
            folium.Marker(
                location=[alert_lat, alert_lon],
                popup=folium.Popup(popup_text, max_width=200),
                icon=folium.Icon(color=color, icon='warning-sign', prefix='glyphicon'),
                tooltip=f"Alert #{i}"
            ).add_to(summary_map)
        
        # Save the map
        output_dir = os.path.dirname(map_file)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        summary_map.save(map_file)
        print(f"Summary map saved to: {map_file}")
        
        return True
        
    except Exception as e:
        print(f"Error creating summary map: {e}")
        return False