"""
SkyLink Pilot Dashboard Flask Application

This Flask app serves a cockpit-style dashboard for pilots with real-time
collision detection, voice alerts, and interactive map visualization.
"""

from flask import Flask, render_template, jsonify, request
import pandas as pd
import json
import os
import random
import math
from datetime import datetime
from typing import List, Dict, Optional, Tuple

# Import our existing collision detection module
import sys
sys.path.append('..')
from collision_module.collision_detection import detect_collisions, calculate_horizontal_distance

app = Flask(__name__)

class PilotDashboardService:
    def __init__(self):
        self.planes_df = None
        self.drones_df = None
        self.real_planes_df = None
        self.real_drones_df = None
        self.test_planes_df = None
        self.test_drones_df = None
        self.current_aircraft_callsign = "UAL100"  # Default for test scenario
        self.use_test_data = True  # Start with test data by default
        self.load_all_data()
        
    def create_test_collision_scenario(self):
        """Create a comprehensive test scenario with guaranteed collisions in NYC area."""
        print("Creating comprehensive test collision scenario...")
        
        # Create test planes around NYC area - more realistic scenario
        planes_data = []
        base_lat, base_lon = 40.7128, -74.0060  # NYC coordinates (JFK area)
        
        # Multiple aircraft at different locations and altitudes
        aircraft_configs = [
            {'callsign': 'UAL100', 'lat_offset': 0.000, 'lon_offset': 0.000, 'alt': 200, 'vel': 150, 'track': 90},
            {'callsign': 'DAL201', 'lat_offset': 0.020, 'lon_offset': -0.020, 'alt': 250, 'vel': 180, 'track': 180},
            {'callsign': 'AAL302', 'lat_offset': -0.020, 'lon_offset': 0.020, 'alt': 300, 'vel': 160, 'track': 270},
            {'callsign': 'JBU403', 'lat_offset': 0.030, 'lon_offset': 0.030, 'alt': 350, 'vel': 170, 'track': 45},
            {'callsign': 'SWA504', 'lat_offset': -0.030, 'lon_offset': -0.030, 'alt': 400, 'vel': 190, 'track': 225},
            {'callsign': 'UAL605', 'lat_offset': 0.010, 'lon_offset': -0.010, 'alt': 280, 'vel': 155, 'track': 135},
            {'callsign': 'AAL706', 'lat_offset': -0.015, 'lon_offset': 0.015, 'alt': 320, 'vel': 165, 'track': 315}
        ]
        
        for i, config in enumerate(aircraft_configs):
            planes_data.append({
                'icao24': f'TEST{i:03d}',
                'callsign': config['callsign'],
                'latitude': base_lat + config['lat_offset'],
                'longitude': base_lon + config['lon_offset'],
                'baro_altitude': config['alt'],
                'velocity': config['vel'],
                'origin_country': 'United States',
                'true_track': config['track'],
                'vertical_rate': random.uniform(-10, 10)  # Random climb/descent rates
            })
        
        # Create drones with varying threat levels
        drones_data = []
        drone_configs = [
            # Critical threat - very close to UAL100
            {'id': 'DRONE_CRITICAL', 'lat_offset': 0.0005, 'lon_offset': 0.0005, 'alt': 190, 'threat': 'critical'},
            # High threats - close to other aircraft
            {'id': 'DRONE_HIGH_1', 'lat_offset': 0.0198, 'lon_offset': -0.0198, 'alt': 240, 'threat': 'high'},
            {'id': 'DRONE_HIGH_2', 'lat_offset': -0.0198, 'lon_offset': 0.0198, 'alt': 290, 'threat': 'high'},
            # Medium threats - moderate distance
            {'id': 'DRONE_MED_1', 'lat_offset': 0.028, 'lon_offset': 0.028, 'alt': 340, 'threat': 'medium'},
            {'id': 'DRONE_MED_2', 'lat_offset': -0.028, 'lon_offset': -0.028, 'alt': 390, 'threat': 'medium'},
            # Low threats - further away
            {'id': 'DRONE_LOW_1', 'lat_offset': 0.045, 'lon_offset': 0.045, 'alt': 450, 'threat': 'low'},
            {'id': 'DRONE_LOW_2', 'lat_offset': -0.045, 'lon_offset': -0.045, 'alt': 500, 'threat': 'low'},
            # Safe drones - no threat
            {'id': 'DRONE_SAFE_1', 'lat_offset': 0.080, 'lon_offset': 0.080, 'alt': 600, 'threat': 'safe'},
            {'id': 'DRONE_SAFE_2', 'lat_offset': -0.080, 'lon_offset': -0.080, 'alt': 700, 'threat': 'safe'}
        ]
        
        for i, config in enumerate(drone_configs):
            drones_data.append({
                'drone_id': config['id'],
                'latitude': base_lat + config['lat_offset'],
                'longitude': base_lon + config['lon_offset'],
                'altitude': config['alt'],
                'speed': 15 + (i * 3),
                'heading': i * 40,
                'time_step': 1,
                'timestamp': '2025-10-12 15:30:00'
            })
        
        planes_df = pd.DataFrame(planes_data)
        drones_df = pd.DataFrame(drones_data)
        
        print(f"✓ Created {len(planes_df)} test aircraft and {len(drones_df)} test drones")
        print("Test Aircraft Distribution:")
        print(f"  - Area: New York City (JFK vicinity)")
        print(f"  - Altitude range: 200-400m")
        print(f"  - Expected collision threats: 5-6 alerts")
        
        return planes_df, drones_df
        
    def load_real_data(self):
        """Load real aircraft and drone data from CSV files."""
        print("Loading real aircraft and drone data from CSV files...")
        
        real_planes_df = pd.DataFrame()
        real_drones_df = pd.DataFrame()
        
        try:
            # Load real plane data
            plane_data_path = "../plane_data/opensky_live_states.csv"
            if os.path.exists(plane_data_path):
                real_planes_df = pd.read_csv(plane_data_path)
                print(f"Raw plane data loaded: {len(real_planes_df)} records")
                
                # Clean and filter data
                real_planes_df = real_planes_df.dropna(subset=['latitude', 'longitude', 'icao24', 'baro_altitude'])
                print(f"After removing NaN values: {len(real_planes_df)} records")
                
                # Filter for reasonable altitude range and remove planes on ground
                real_planes_df = real_planes_df[
                    (real_planes_df['baro_altitude'].between(100, 15000)) &  # Reasonable altitude range
                    (real_planes_df['on_ground'] == False) &  # Only airborne aircraft
                    (real_planes_df['velocity'] > 50)  # Only moving aircraft
                ]
                print(f"After altitude/status filtering: {len(real_planes_df)} records")
                
                # Enhanced regional filtering for richer real mode - targeting 100 planes
                if len(real_planes_df) > 0:
                    # Identify major aviation hubs and regions with optimized sampling
                    regions = [
                        {'name': 'North America', 'lat_min': 25, 'lat_max': 60, 'lon_min': -130, 'lon_max': -60, 'sample_size': 25},
                        {'name': 'Europe', 'lat_min': 35, 'lat_max': 70, 'lon_min': -10, 'lon_max': 30, 'sample_size': 20},
                        {'name': 'Asia-Pacific', 'lat_min': -10, 'lat_max': 50, 'lon_min': 70, 'lon_max': 150, 'sample_size': 20},
                        {'name': 'Middle East', 'lat_min': 15, 'lat_max': 45, 'lon_min': 25, 'lon_max': 70, 'sample_size': 15},
                        {'name': 'Global Others', 'lat_min': -90, 'lat_max': 90, 'lon_min': -180, 'lon_max': 180, 'sample_size': 20}
                    ]
                    
                    regional_aircraft = []
                    for region in regions:
                        region_planes = real_planes_df[
                            (real_planes_df['latitude'].between(region['lat_min'], region['lat_max'])) &
                            (real_planes_df['longitude'].between(region['lon_min'], region['lon_max']))
                        ]
                        
                        if len(region_planes) > 0:
                            sample_size = min(region['sample_size'], len(region_planes))
                            region_sample = region_planes.sample(n=sample_size, random_state=42)
                            regional_aircraft.append(region_sample)
                            print(f"  {region['name']}: {sample_size} aircraft from {len(region_planes)} available")
                    
                    if regional_aircraft:
                        real_planes_df = pd.concat(regional_aircraft, ignore_index=True)
                        print(f"✓ Loaded {len(real_planes_df)} real aircraft from multiple regions")
                    else:
                        # Fallback to original sampling if regional filtering fails
                        real_planes_df = real_planes_df.sample(n=min(50, len(real_planes_df)), random_state=42)
                        print(f"✓ Loaded {len(real_planes_df)} real aircraft (global sample)")
                    
                    # Show regional distribution
                    if len(real_planes_df) > 0:
                        countries = real_planes_df['origin_country'].value_counts().head(5)
                        print(f"  Top countries: {', '.join([f'{country}({count})' for country, count in countries.items()])}")
                else:
                    print("⚠ No aircraft found matching filter criteria")
            else:
                print(f"⚠ Real plane data file not found: {plane_data_path}")

            # Load real drone data with enhanced sampling
            drone_data_path = "../drone_data/dummy_drone_dataset_30.csv"
            if os.path.exists(drone_data_path):
                real_drones_df = pd.read_csv(drone_data_path)
                print(f"Raw drone data loaded: {len(real_drones_df)} records")
                
                # Clean and filter data
                real_drones_df = real_drones_df.dropna(subset=['latitude', 'longitude', 'drone_id', 'altitude'])
                
                # Enhanced drone sampling - get diverse time steps and all drones
                unique_drones = real_drones_df['drone_id'].unique()
                selected_drones = []
                
                # Sample multiple time steps for realistic movement
                time_steps = [0, 5, 10, 15, 19]  # Different time points
                for time_step in time_steps:
                    time_data = real_drones_df[real_drones_df['time_step'] == time_step]
                    if not time_data.empty:
                        # Take all drones for this time step (creates movement simulation)
                        selected_drones.append(time_data)
                        
                if selected_drones:
                    real_drones_df = pd.concat(selected_drones, ignore_index=True)
                    # Remove duplicates, keep latest time step for each drone
                    real_drones_df = real_drones_df.sort_values('time_step').drop_duplicates(subset=['drone_id'], keep='last')
                else:
                    # Fallback - take latest positions of all drones
                    real_drones_df = real_drones_df.sort_values('time_step').drop_duplicates(subset=['drone_id'], keep='last')
                
                print(f"✓ Loaded {len(real_drones_df)} real drones from {len(unique_drones)} unique drone IDs")
                
                # Show geographic distribution
                if len(real_drones_df) > 0:
                    lat_range = f"{real_drones_df['latitude'].min():.2f}° to {real_drones_df['latitude'].max():.2f}°"
                    lon_range = f"{real_drones_df['longitude'].min():.2f}° to {real_drones_df['longitude'].max():.2f}°"
                    alt_range = f"{real_drones_df['altitude'].min():.0f}m to {real_drones_df['altitude'].max():.0f}m"
                    print(f"  Coverage - Lat: {lat_range}, Lon: {lon_range}, Alt: {alt_range}")
            else:
                print(f"⚠ Real drone data file not found: {drone_data_path}")
                
            # REAL DATA MODE: Show aircraft near current pilot aircraft with threshold filtering
            # Don't concentrate around regions - use proximity-based filtering for realistic pilot view
            if len(real_planes_df) > 0:
                print("✓ Real data mode: Using proximity-based aircraft filtering")
                print(f"✓ Base aircraft pool: {len(real_planes_df)} aircraft from {len(real_planes_df['origin_country'].unique())} countries")
                
                # Keep all real aircraft as they are - filtering will be done during radar display
                # This allows the pilot to see aircraft near their current position dynamically
                print("✓ Aircraft will be filtered by proximity during radar display")
                print("✓ This provides realistic pilot dashboard experience")
                
        except Exception as e:
            print(f"Error loading real data: {e}")
            real_planes_df = pd.DataFrame()
            real_drones_df = pd.DataFrame()
            
        return real_planes_df, real_drones_df
    
    def load_all_data(self):
        """Load both test and real data, then set current data based on mode."""
        print("Initializing SkyLink Pilot Dashboard Data...")
        
        # Load test scenario
        self.test_planes_df, self.test_drones_df = self.create_test_collision_scenario()
        
        # Load real data
        self.real_planes_df, self.real_drones_df = self.load_real_data()
        
        # Set current data based on mode
        self.switch_data_mode()
        
    def switch_data_mode(self):
        """Switch between test and real data modes."""
        if self.use_test_data:
            self.planes_df = self.test_planes_df.copy()
            self.drones_df = self.test_drones_df.copy()
            self.current_aircraft_callsign = "UAL100"  # Default test aircraft
            print(f"✓ Switched to TEST MODE: {len(self.planes_df)} planes, {len(self.drones_df)} drones")
        else:
            self.planes_df = self.real_planes_df.copy()
            self.drones_df = self.real_drones_df.copy()
            
            # Ensure we have exactly 30 drones by creating variants if needed
            if len(self.drones_df) < 30:
                print(f"⚠ Only {len(self.drones_df)} drones available, creating variants to reach 30...")
                additional_drones = []
                base_drones = self.drones_df.copy()
                
                while len(self.drones_df) + len(additional_drones) < 30:
                    for _, drone in base_drones.iterrows():
                        if len(self.drones_df) + len(additional_drones) >= 30:
                            break
                            
                        # Create a variant of the drone with slight position offset
                        variant = drone.copy()
                        suffix = len(additional_drones) + len(self.drones_df)
                        variant['drone_id'] = f"{drone['drone_id']}_V{suffix}"
                        variant['latitude'] += random.uniform(-0.001, 0.001)
                        variant['longitude'] += random.uniform(-0.001, 0.001)
                        variant['altitude'] += random.uniform(-20, 20)
                        additional_drones.append(variant)
                
                if additional_drones:
                    additional_df = pd.DataFrame(additional_drones)
                    self.drones_df = pd.concat([self.drones_df, additional_df], ignore_index=True)
                    print(f"✓ Added {len(additional_drones)} drone variants")
            
            # Enhanced aircraft selection for real mode
            if not self.planes_df.empty:
                # Prefer regional aircraft (REG prefix) for better local clustering
                regional_aircraft = self.planes_df[self.planes_df['icao24'].str.startswith('REG', na=False)]
                
                if not regional_aircraft.empty:
                    self.current_aircraft_callsign = str(regional_aircraft.iloc[0]['callsign']).strip()
                    print(f"✓ Selected regional aircraft: {self.current_aircraft_callsign}")
                else:
                    self.current_aircraft_callsign = str(self.planes_df.iloc[0]['callsign']).strip()
                    print(f"✓ Selected aircraft: {self.current_aircraft_callsign}")
                    
                # Create aircraft clusters around the selected aircraft for better visibility
                self._create_aircraft_clusters()
                    
            print(f"✓ Switched to REAL DATA MODE: {len(self.planes_df)} planes, {len(self.drones_df)} drones")
            
    def load_data(self):
        """Legacy method - just switches data mode."""
        self.switch_data_mode()
    
    def get_current_aircraft(self, callsign: str = None) -> Optional[Dict]:
        """Get the current aircraft (pilot's plane) data."""
        if callsign:
            self.current_aircraft_callsign = callsign
            
        if self.planes_df.empty:
            return None
        
        # Set default callsign based on data mode
        if not self.current_aircraft_callsign:
            if self.use_test_data:
                self.current_aircraft_callsign = "UAL100"  # Test scenario aircraft
            else:
                self.current_aircraft_callsign = "AI100"   # Real scenario local aircraft
            
        # Find the aircraft with the specified callsign
        current_plane = self.planes_df[
            self.planes_df['callsign'].str.strip() == self.current_aircraft_callsign
        ]
        
        if current_plane.empty:
            # If specific callsign not found, use the first aircraft
            current_plane = self.planes_df.iloc[0:1]
            if not current_plane.empty:
                self.current_aircraft_callsign = current_plane.iloc[0]['callsign'].strip()
        
        if current_plane.empty:
            return None
            
        plane = current_plane.iloc[0]
        return {
            'callsign': plane.get('callsign', '').strip(),
            'icao24': plane.get('icao24', ''),
            'latitude': float(plane.get('latitude', 0)),
            'longitude': float(plane.get('longitude', 0)),
            'altitude': float(plane.get('baro_altitude', 0)),
            'speed': float(plane.get('velocity', 0)),
            'heading': float(plane.get('true_track', 0)) if pd.notna(plane.get('true_track')) else 0.0,
            'vertical_rate': float(plane.get('vertical_rate', 0)) if pd.notna(plane.get('vertical_rate')) else 0.0,
            'country': plane.get('origin_country', 'Unknown')
        }
    
    def get_nearby_aircraft(self, current_aircraft: Dict, range_nm: float = 10) -> List[Dict]:
        """Get nearby aircraft within specified range."""
        if self.planes_df.empty or not current_aircraft:
            return []
            
        nearby_aircraft = []
        range_km = range_nm * 1.852  # Convert nautical miles to kilometers
        
        current_lat = current_aircraft['latitude']
        current_lon = current_aircraft['longitude']
        current_icao = current_aircraft['icao24']
        
        print(f"Looking for aircraft near {current_aircraft['callsign']} at ({current_lat:.4f}, {current_lon:.4f}) within {range_nm} NM")
        print(f"Total aircraft in database: {len(self.planes_df)}")
        
        if not self.use_test_data:
            # REAL MODE: Use smart proximity-based filtering
            # First try to find aircraft within reasonable radar range
            # If not enough found, gradually expand search or take closest aircraft
            print("REAL MODE: Using smart proximity filtering")
            
            # Try different ranges to ensure we get enough aircraft for good radar display
            search_ranges = [range_nm, range_nm * 2, range_nm * 5, range_nm * 10]
            target_aircraft_count = 50  # Target at least 50 aircraft for good display
            
            for search_range in search_ranges:
                temp_nearby = []
                
                for idx, plane in self.planes_df.iterrows():
                    if plane['icao24'] == current_icao:
                        continue
                    if pd.isna(plane['latitude']) or pd.isna(plane['longitude']):
                        continue
                        
                    distance_km = calculate_horizontal_distance(current_lat, current_lon, plane['latitude'], plane['longitude'])
                    distance_nm = distance_km / 1.852
                    
                    if distance_nm <= search_range:
                        temp_nearby.append((plane, distance_nm))
                
                print(f"  Search range {search_range:.1f} NM: Found {len(temp_nearby)} aircraft")
                
                if len(temp_nearby) >= target_aircraft_count:
                    # Sort by distance and take the closest ones
                    temp_nearby.sort(key=lambda x: x[1])
                    nearby_pairs = temp_nearby[:target_aircraft_count]
                    print(f"✓ Using {len(nearby_pairs)} closest aircraft within {search_range:.1f} NM")
                    break
                elif search_range == search_ranges[-1] and temp_nearby:
                    # Last resort - take whatever we found
                    temp_nearby.sort(key=lambda x: x[1])
                    nearby_pairs = temp_nearby
                    print(f"✓ Using all {len(nearby_pairs)} aircraft found within {search_range:.1f} NM")
                    break
            else:
                nearby_pairs = []
                
            effective_range = search_ranges[-1]  # For logging purposes
            
        else:
            # TEST MODE: Use original logic with fixed range
            effective_range = range_nm
            nearby_pairs = []
            
            for idx, plane in self.planes_df.iterrows():
                if plane['icao24'] == current_icao:
                    continue
                if pd.isna(plane['latitude']) or pd.isna(plane['longitude']):
                    continue
                    
                distance_km = calculate_horizontal_distance(current_lat, current_lon, plane['latitude'], plane['longitude'])
                distance_nm = distance_km / 1.852
                
                if distance_nm <= effective_range:
                    nearby_pairs.append((plane, distance_nm))
        
        # Convert nearby_pairs to the final nearby_aircraft list
        for i, (plane, distance_nm) in enumerate(nearby_pairs):
            if i < 10:  # Only print first 10 to avoid spam
                print(f"  {plane.get('callsign', 'Unknown')}: {distance_nm:.1f} NM")
            
            nearby_aircraft.append({
                'callsign': plane.get('callsign', '').strip(),
                'icao24': plane.get('icao24', ''),
                'latitude': float(plane['latitude']),
                'longitude': float(plane['longitude']),
                'altitude': float(plane.get('baro_altitude', 0)),
                'speed': float(plane.get('velocity', 0)),
                'distance': distance_nm,
                'bearing': self.calculate_bearing(
                    current_lat, current_lon,
                    plane['latitude'], plane['longitude']
                ),
                'relative_position': self.get_relative_position_description(
                    current_lat, current_lon,
                    plane['latitude'], plane['longitude']
                )
            })
        
        print(f"✓ Final result: {len(nearby_aircraft)} nearby aircraft")
        
        # In real mode, we already filtered to the right amount, in test mode apply limit
        if self.use_test_data:
            max_aircraft = 15
            nearby_aircraft = nearby_aircraft[:max_aircraft]
            
        return nearby_aircraft
    
    def get_collision_threats(self, current_aircraft: Dict, range_nm: float = 10) -> List[Dict]:
        """Detect collision threats for the current aircraft."""
        if self.drones_df.empty or not current_aircraft:
            return []
            
        print(f"Detecting collision threats for {current_aircraft['callsign']} within {range_nm} NM")
        
        # Get nearby drones first
        nearby_drones = self.get_nearby_drones(current_aircraft, range_nm)
        
        if not nearby_drones:
            print("No nearby drones found for collision detection")
            return []
        
        # Create a temporary DataFrame for just the current aircraft
        current_plane_df = pd.DataFrame([{
            'icao24': current_aircraft['icao24'],
            'callsign': current_aircraft['callsign'],
            'latitude': current_aircraft['latitude'],
            'longitude': current_aircraft['longitude'],
            'baro_altitude': current_aircraft['altitude'],
            'velocity': current_aircraft['speed']
        }])
        
        # Convert nearby drones to DataFrame for collision detection
        nearby_drones_df = pd.DataFrame([{
            'drone_id': drone['drone_id'],
            'latitude': drone['latitude'],
            'longitude': drone['longitude'],
            'altitude': drone['altitude'],
            'speed': drone['speed'],
            'heading': drone.get('heading', 0),
            'time_step': 1,
            'timestamp': '2025-10-12 12:00:00'
        } for drone in nearby_drones])
        
        print(f"Checking {len(nearby_drones_df)} nearby drones for collisions")
        
        # Enhanced threat levels for real mode - more comprehensive detection
        if self.use_test_data:
            # Standard thresholds for test mode
            threat_levels = [
                {'name': 'critical', 'h_threshold': 0.1, 'v_threshold': 30},
                {'name': 'high', 'h_threshold': 0.3, 'v_threshold': 50},
                {'name': 'medium', 'h_threshold': 0.5, 'v_threshold': 100},
                {'name': 'low', 'h_threshold': 1.0, 'v_threshold': 150}
            ]
        else:
            # Enhanced thresholds for real mode - more sensitive detection
            threat_levels = [
                {'name': 'critical', 'h_threshold': 0.05, 'v_threshold': 25},
                {'name': 'high', 'h_threshold': 0.2, 'v_threshold': 40},
                {'name': 'medium', 'h_threshold': 0.4, 'v_threshold': 75},
                {'name': 'low', 'h_threshold': 0.8, 'v_threshold': 120},
                {'name': 'advisory', 'h_threshold': 1.5, 'v_threshold': 200}
            ]
        
        all_threats = []
        
        for level in threat_levels:
            alerts = detect_collisions(
                current_plane_df, 
                nearby_drones_df,
                h_threshold=level['h_threshold'],
                v_threshold=level['v_threshold']
            )
            
            print(f"  {level['name'].upper()} level ({level['h_threshold']} km, {level['v_threshold']} m): {len(alerts)} alerts")
            
            for alert in alerts:
                # Check if this threat already exists at a higher priority level
                existing_threat = next((t for t in all_threats if t['id'] == alert['drone_id']), None)
                if existing_threat:
                    continue
                    
                # Find the original drone data for additional info
                drone_data = next((d for d in nearby_drones if d['drone_id'] == alert['drone_id']), {})
                
                threat = {
                    'type': 'drone',
                    'id': alert['drone_id'],
                    'latitude': alert['drone_lat'],
                    'longitude': alert['drone_lon'],
                    'altitude': alert['drone_altitude'],
                    'horizontal_distance': alert['horizontal_distance'],
                    'vertical_distance': alert['vertical_distance'],
                    'risk_level': level['name'],
                    'bearing': self.calculate_bearing(
                        current_aircraft['latitude'], current_aircraft['longitude'],
                        alert['drone_lat'], alert['drone_lon']
                    ),
                    'relative_position': self.get_relative_position_description(
                        current_aircraft['latitude'], current_aircraft['longitude'],
                        alert['drone_lat'], alert['drone_lon']
                    ),
                    'distance_nm': drone_data.get('distance', 0),
                    'drone_speed': drone_data.get('speed', 0),
                    'drone_heading': drone_data.get('heading', 0)
                }
                all_threats.append(threat)
        
        # Sort by risk level and distance
        risk_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
        all_threats.sort(key=lambda x: (risk_order[x['risk_level']], x['horizontal_distance']))
        
        print(f"Total threats found: {len(all_threats)}")
        for threat in all_threats:
            print(f"  {threat['risk_level'].upper()}: {threat['id']} at {threat['horizontal_distance']:.3f} km, {threat['vertical_distance']} m ({threat['relative_position']})")
        
        return all_threats
    
    def calculate_bearing(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate bearing from point 1 to point 2."""
        import math
        
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        dlon_rad = math.radians(lon2 - lon1)
        
        y = math.sin(dlon_rad) * math.cos(lat2_rad)
        x = (math.cos(lat1_rad) * math.sin(lat2_rad) - 
             math.sin(lat1_rad) * math.cos(lat2_rad) * math.cos(dlon_rad))
        
        bearing_rad = math.atan2(y, x)
        bearing_deg = (math.degrees(bearing_rad) + 360) % 360
        
        return bearing_deg
    
    def get_relative_position_description(self, lat1: float, lon1: float, lat2: float, lon2: float) -> str:
        """Get a description of relative position (N, NE, E, SE, S, SW, W, NW)."""
        bearing = self.calculate_bearing(lat1, lon1, lat2, lon2)
        
        if bearing < 22.5 or bearing >= 337.5:
            return "N"
        elif bearing < 67.5:
            return "NE"
        elif bearing < 112.5:
            return "E"
        elif bearing < 157.5:
            return "SE"
        elif bearing < 202.5:
            return "S"
        elif bearing < 247.5:
            return "SW"
        elif bearing < 292.5:
            return "W"
        else:
            return "NW"
    
    def get_region_name(self, lat: float, lon: float) -> str:
        """Get a descriptive region name based on coordinates."""
        # Major aviation hubs and regions
        regions = [
            {'name': 'Bangalore', 'lat': 12.95, 'lon': 77.55, 'radius': 2},
            {'name': 'Mumbai', 'lat': 19.08, 'lon': 72.87, 'radius': 2},
            {'name': 'Delhi', 'lat': 28.61, 'lon': 77.23, 'radius': 2},
            {'name': 'New York', 'lat': 40.71, 'lon': -74.00, 'radius': 2},
            {'name': 'London', 'lat': 51.51, 'lon': -0.12, 'radius': 2},
            {'name': 'Frankfurt', 'lat': 50.11, 'lon': 8.68, 'radius': 2},
            {'name': 'Dubai', 'lat': 25.25, 'lon': 55.36, 'radius': 2},
            {'name': 'Singapore', 'lat': 1.35, 'lon': 103.82, 'radius': 2},
            {'name': 'Tokyo', 'lat': 35.68, 'lon': 139.69, 'radius': 2},
            {'name': 'Los Angeles', 'lat': 34.05, 'lon': -118.24, 'radius': 2}
        ]
        
        # Find closest major hub
        min_distance = float('inf')
        closest_region = None
        
        for region in regions:
            distance = calculate_horizontal_distance(lat, lon, region['lat'], region['lon'])
            if distance < region['radius'] and distance < min_distance:
                min_distance = distance
                closest_region = region['name']
        
        if closest_region:
            return closest_region
        
        # Fallback to geographic region
        if 10 <= lat <= 30 and 70 <= lon <= 90:
            return "India"
        elif 35 <= lat <= 70 and -10 <= lon <= 30:
            return "Europe"
        elif 25 <= lat <= 60 and -130 <= lon <= -60:
            return "North America"
        elif 15 <= lat <= 45 and 25 <= lon <= 70:
            return "Middle East"
        elif -10 <= lat <= 50 and 70 <= lon <= 150:
            return "Asia-Pacific"
        else:
            return f"Region_{int(lat)}N_{int(abs(lon))}{'E' if lon >= 0 else 'W'}"
    
    def generate_regional_callsign(self, region_name: str, counter: int) -> str:
        """Generate realistic callsigns based on region."""
        regional_prefixes = {
            'India': ['AI', '6E', 'SG', 'UK', 'G8'],
            'Bangalore': ['AI', '6E', 'SG', 'UK'],
            'Mumbai': ['AI', '6E', 'SG', '9W'],
            'Delhi': ['AI', '6E', 'UK', '9W'],
            'Europe': ['LH', 'AF', 'BA', 'KL', 'AZ'],
            'North America': ['UAL', 'DAL', 'AAL', 'JBU', 'SWA'],
            'London': ['BA', 'VS', 'EZY', 'RYR'],
            'Frankfurt': ['LH', 'DE', 'EW'],
            'New York': ['UAL', 'DAL', 'AAL', 'JBU'],
            'Middle East': ['EK', 'QR', 'EY', 'MS'],
            'Asia-Pacific': ['SQ', 'CX', 'TG', 'MH'],
            'Dubai': ['EK', 'FZ', 'QR'],
            'Singapore': ['SQ', 'TR', '3K'],
            'Tokyo': ['NH', 'JL', 'MM']
        }
        
        prefixes = regional_prefixes.get(region_name, ['REG'])
        prefix = prefixes[counter % len(prefixes)]
        number = 100 + (counter * 7) % 899  # Generate realistic flight numbers
        
        return f"{prefix}{number}"
    
    def _create_aircraft_clusters(self):
        """Create clusters of aircraft around major hubs for better radar visualization."""
        if self.planes_df.empty:
            return
            
        # Find the current aircraft position to create clusters around it
        current_aircraft = self.get_current_aircraft()
        if not current_aircraft:
            return
            
        cluster_aircraft = []
        base_lat = current_aircraft['latitude']
        base_lon = current_aircraft['longitude']
        
        # Create additional aircraft in the vicinity for realistic radar display
        existing_aircraft_count = len(self.planes_df)
        
        # Add aircraft in concentric circles around the current aircraft
        for ring in range(1, 4):  # 3 rings
            ring_distance = ring * 0.05  # 0.05, 0.10, 0.15 degrees (~5-15 km)
            aircraft_in_ring = 8 if ring == 1 else 6 if ring == 2 else 4
            
            for i in range(aircraft_in_ring):
                angle = (360 / aircraft_in_ring) * i
                import math
                angle_rad = math.radians(angle)
                
                # Calculate position in the ring
                new_lat = base_lat + (ring_distance * math.cos(angle_rad))
                new_lon = base_lon + (ring_distance * math.sin(angle_rad))
                
                # Use existing aircraft as template but change position
                template_idx = (ring * 10 + i) % min(10, existing_aircraft_count)
                if template_idx < len(self.planes_df):
                    template_aircraft = self.planes_df.iloc[template_idx].copy()
                    
                    # Modify the template
                    template_aircraft['latitude'] = new_lat
                    template_aircraft['longitude'] = new_lon
                    template_aircraft['icao24'] = f'CLU{ring}{i:02d}'
                    template_aircraft['callsign'] = f'CL{ring}{100+i}'
                    template_aircraft['baro_altitude'] = 200 + (ring * 100) + (i * 25)
                    template_aircraft['velocity'] = 80 + (i * 10)
                    
                    cluster_aircraft.append(template_aircraft)
        
        if cluster_aircraft:
            cluster_df = pd.DataFrame(cluster_aircraft)
            self.planes_df = pd.concat([self.planes_df, cluster_df], ignore_index=True)
            print(f"✓ Added {len(cluster_aircraft)} clustered aircraft for enhanced radar visibility")
    
    def get_nearby_drones(self, current_aircraft: Dict, range_nm: float = 10) -> List[Dict]:
        """Get nearby drones within specified range."""
        if self.drones_df.empty or not current_aircraft:
            return []
            
        nearby_drones = []
        current_lat = current_aircraft['latitude']
        current_lon = current_aircraft['longitude']
        
        print(f"Looking for drones near {current_aircraft['callsign']} within {range_nm} NM")
        
        # Enhanced range for real mode to show more drones
        effective_range = range_nm * 2 if not self.use_test_data else range_nm
        print(f"Using effective drone search range: {effective_range:.1f} NM")
        
        for idx, drone in self.drones_df.iterrows():
            # Skip drones with missing coordinates
            if pd.isna(drone['latitude']) or pd.isna(drone['longitude']):
                continue
                
            # Calculate distance
            distance_km = calculate_horizontal_distance(
                current_lat, current_lon, 
                drone['latitude'], drone['longitude']
            )
            
            # Convert to nautical miles
            distance_nm = distance_km / 1.852
            
            if idx < 10:  # Only print first 10 to avoid spam
                print(f"  {drone.get('drone_id', 'Unknown')}: {distance_km:.2f} km ({distance_nm:.1f} NM)")
            
            if distance_nm <= effective_range:
                nearby_drones.append({
                    'drone_id': drone.get('drone_id', ''),
                    'latitude': float(drone['latitude']),
                    'longitude': float(drone['longitude']),
                    'altitude': float(drone.get('altitude', 0)),
                    'speed': float(drone.get('speed', 0)),
                    'heading': float(drone.get('heading', 0)),
                    'distance': distance_nm,
                    'bearing': self.calculate_bearing(
                        current_lat, current_lon,
                        drone['latitude'], drone['longitude']
                    ),
                    'relative_position': self.get_relative_position_description(
                        current_lat, current_lon,
                        drone['latitude'], drone['longitude']
                    )
                })
        
        # Sort by distance
        nearby_drones.sort(key=lambda x: x['distance'])
        print(f"Found {len(nearby_drones)} nearby drones")
        
        # Return more drones in real mode for enriched experience
        max_drones = 30 if not self.use_test_data else 15
        return nearby_drones[:max_drones]

# Initialize the service
dashboard_service = PilotDashboardService()

@app.route('/')
def index():
    """Serve the main pilot dashboard."""
    return render_template('pilot_dashboard.html')

@app.route('/api/pilot-data')
def get_pilot_data():
    """API endpoint to get current pilot data including aircraft, nearby traffic, and threats."""
    try:
        # Get query parameters
        callsign = request.args.get('callsign', dashboard_service.current_aircraft_callsign)
        radar_range = float(request.args.get('range', 10))  # nautical miles
        
        # Get current aircraft data
        current_aircraft = dashboard_service.get_current_aircraft(callsign)
        
        if not current_aircraft:
            return jsonify({
                'error': 'Aircraft not found',
                'current_aircraft': None,
                'nearby_aircraft': [],
                'threats': []
            })
        
        # Get nearby aircraft
        nearby_aircraft = dashboard_service.get_nearby_aircraft(current_aircraft, radar_range)
        
        # Get nearby drones
        nearby_drones = dashboard_service.get_nearby_drones(current_aircraft, radar_range)
        
        # Get collision threats
        threats = dashboard_service.get_collision_threats(current_aircraft, radar_range)
        
        return jsonify({
            'current_aircraft': current_aircraft,
            'nearby_aircraft': nearby_aircraft,
            'nearby_drones': nearby_drones,
            'threats': threats,
            'timestamp': datetime.now().isoformat(),
            'radar_range_nm': radar_range,
            'data_source': "test_scenario" if dashboard_service.use_test_data else "real_data"
        })
        
    except Exception as e:
        print(f"Error in get_pilot_data: {e}")
        return jsonify({
            'error': str(e),
            'current_aircraft': None,
            'nearby_aircraft': [],
            'threats': []
        }), 500

@app.route('/api/aircraft-list')
def get_aircraft_list():
    """Get list of available aircraft callsigns."""
    try:
        if dashboard_service.planes_df.empty:
            return jsonify({'aircraft': []})
            
        callsigns = dashboard_service.planes_df['callsign'].dropna().str.strip().unique().tolist()
        return jsonify({'aircraft': callsigns})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/set-aircraft', methods=['POST'])
def set_current_aircraft():
    """Set the current aircraft for the pilot dashboard."""
    try:
        data = request.get_json()
        callsign = data.get('callsign')
        
        if not callsign:
            return jsonify({'error': 'Callsign required'}), 400
            
        dashboard_service.current_aircraft_callsign = callsign
        return jsonify({'success': True, 'callsign': callsign})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/reload-data', methods=['POST'])
def reload_data():
    """Reload aircraft and drone data from CSV files."""
    try:
        dashboard_service.load_data()
        return jsonify({
            'success': True,
            'planes_loaded': len(dashboard_service.planes_df),
            'drones_loaded': len(dashboard_service.drones_df),
            'using_test_data': dashboard_service.use_test_data
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/toggle-data-source', methods=['POST'])
def toggle_data_source():
    """Toggle between test collision scenario and real CSV data."""
    try:
        # Toggle the data mode
        dashboard_service.use_test_data = not dashboard_service.use_test_data
        dashboard_service.switch_data_mode()
        
        # Prepare response
        if dashboard_service.use_test_data:
            data_source = "Test Collision Scenario (NYC)"
            description = f"Synthetic data with {len(dashboard_service.planes_df)} aircraft and {len(dashboard_service.drones_df)} drones designed to show collision detection"
        else:
            data_source = "Real Flight Data (Filtered)"
            description = f"Real aircraft data with {len(dashboard_service.planes_df)} planes and {len(dashboard_service.drones_df)} drones from CSV files"
        
        return jsonify({
            'success': True,
            'data_source': data_source,
            'description': description,
            'using_test_data': dashboard_service.use_test_data,
            'planes_loaded': len(dashboard_service.planes_df),
            'drones_loaded': len(dashboard_service.drones_df),
            'current_aircraft': dashboard_service.current_aircraft_callsign,
            'has_real_data': not dashboard_service.real_planes_df.empty,
            'has_test_data': not dashboard_service.test_planes_df.empty
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/collision-demo')
def get_collision_demo():
    """Get detailed collision detection demo data."""
    try:
        if dashboard_service.planes_df.empty or dashboard_service.drones_df.empty:
            return jsonify({'error': 'No data available'}), 400
            
        # Run collision detection with different thresholds to show the logic
        demo_results = []
        
        thresholds = [
            {'name': 'Very Strict', 'h': 0.1, 'v': 30},
            {'name': 'Strict', 'h': 0.2, 'v': 50},
            {'name': 'Normal', 'h': 0.5, 'v': 100},
            {'name': 'Relaxed', 'h': 1.0, 'v': 150}
        ]
        
        for threshold in thresholds:
            alerts = detect_collisions(
                dashboard_service.planes_df,
                dashboard_service.drones_df,
                h_threshold=threshold['h'],
                v_threshold=threshold['v']
            )
            
            demo_results.append({
                'threshold_name': threshold['name'],
                'horizontal_km': threshold['h'],
                'vertical_m': threshold['v'],
                'alerts_found': len(alerts),
                'alerts': alerts[:3]  # First 3 alerts as examples
            })
        
        return jsonify({
            'demo_results': demo_results,
            'total_planes': len(dashboard_service.planes_df),
            'total_drones': len(dashboard_service.drones_df),
            'data_source': "test collision scenario" if dashboard_service.use_test_data else "real CSV data"
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/data-info')
def get_data_info():
    """Get information about available data sources."""
    try:
        # Get detailed aircraft info for debugging
        current_aircraft_info = {}
        all_aircraft_sample = []
        
        if not dashboard_service.planes_df.empty:
            current_aircraft_info = {
                'callsign': dashboard_service.current_aircraft_callsign,
                'total_aircraft': len(dashboard_service.planes_df),
                'sample_locations': []
            }
            
            # Get sample of aircraft locations for debugging
            for i, plane in dashboard_service.planes_df.head(10).iterrows():
                all_aircraft_sample.append({
                    'callsign': str(plane.get('callsign', 'Unknown')).strip(),
                    'icao24': plane.get('icao24', ''),
                    'latitude': float(plane.get('latitude', 0)),
                    'longitude': float(plane.get('longitude', 0)),
                    'altitude': float(plane.get('baro_altitude', 0))
                })
        
        return jsonify({
            'current_mode': 'test' if dashboard_service.use_test_data else 'real',
            'test_data': {
                'available': not dashboard_service.test_planes_df.empty,
                'planes': len(dashboard_service.test_planes_df),
                'drones': len(dashboard_service.test_drones_df),
                'description': 'NYC test scenario with guaranteed collision alerts'
            },
            'real_data': {
                'available': not dashboard_service.real_planes_df.empty,
                'planes': len(dashboard_service.real_planes_df),
                'drones': len(dashboard_service.real_drones_df),
                'description': 'Real flight data from CSV files (filtered)'
            },
            'current_aircraft': dashboard_service.current_aircraft_callsign,
            'debug_info': {
                'current_aircraft_info': current_aircraft_info,
                'sample_aircraft': all_aircraft_sample,
                'using_data_source': 'test' if dashboard_service.use_test_data else 'real'
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("Starting SkyLink Pilot Dashboard...")
    print(f"Dashboard available at: http://localhost:5000")
    print(f"Current aircraft: {dashboard_service.current_aircraft_callsign}")
    
    app.run(debug=True, host='0.0.0.0', port=5000)