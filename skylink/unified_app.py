"""
SkyLink Unified Web Application

Single webpage hub that provides access to both drone and pilot dashboards
while preserving all existing core logic and functionality.
"""

from flask import Flask, render_template, jsonify, request, redirect, url_for, Response
import pandas as pd
import json
import os
import random
import math
from datetime import datetime
from typing import List, Dict, Optional, Tuple

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # dotenv not available, use system environment variables
    pass

# Import existing modules (preserving core logic)
import sys
sys.path.append('.')
from collision_module.collision_detection import detect_collisions, calculate_horizontal_distance, get_collision_summary
from visualization import plot_airspace, create_summary_map

# Try to import drone dashboard modules - create fallbacks if not available
try:
    from drone_alerts.drone_dashboard import DroneDashboard
    from drone_alerts.alert_translator import DroneAlertTranslator
    DRONE_DASHBOARD_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Drone dashboard modules not available: {e}")
    DRONE_DASHBOARD_AVAILABLE = False
    
    # Create fallback classes
    class DroneDashboard:
        def __init__(self):
            self.alert_translator = DroneAlertTranslator()
            
        def _create_dashboard_html(self, alerts_data, drone_data):
            return "<html><body><h1>Drone Dashboard Not Available</h1><p>Please ensure drone_alerts module is installed.</p></body></html>"
    
    class DroneAlertTranslator:
        def process_multiple_alerts(self, drone_data, plane_data):
            return []

app = Flask(__name__, template_folder='templates', static_folder='templates/static')

class SkyLinkUnifiedService:
    def __init__(self):
        """Initialize unified service with both pilot and drone capabilities."""
        # Preserve existing pilot dashboard service logic
        self.planes_df = None
        self.drones_df = None
        self.test_planes_df = None
        self.test_drones_df = None
        self.real_planes_df = None
        self.real_drones_df = None
        self.current_aircraft_callsign = "UAL100"
        self.use_test_data = True
        
        # Add drone dashboard components
        if DRONE_DASHBOARD_AVAILABLE:
            self.drone_dashboard = DroneDashboard()
            self.alert_translator = DroneAlertTranslator()
        else:
            self.drone_dashboard = DroneDashboard()  # Fallback version
            self.alert_translator = DroneAlertTranslator()  # Fallback version
        
        # Load all data
        self.load_all_data()
        
    def create_test_collision_scenario(self):
        """Create comprehensive test scenario (preserving existing logic)."""
        print("Creating comprehensive test collision scenario...")
        
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
                'vertical_rate': (-5 + i * 2.5),
                'on_ground': False
            })
        
        # Create strategic drone positions for different collision scenarios
        drones_data = []
        drone_scenarios = [
            {'id': 'DRONE_CRITICAL', 'lat_offset': 0.0006, 'lon_offset': 0.0006, 'alt': 190, 'desc': 'Critical collision threat'},
            {'id': 'DRONE_HIGH_1', 'lat_offset': 0.0200, 'lon_offset': -0.0180, 'alt': 230, 'desc': 'High risk - near DAL201'},
            {'id': 'DRONE_HIGH_2', 'lat_offset': -0.0180, 'lon_offset': 0.0200, 'alt': 280, 'desc': 'High risk - near AAL302'},
            {'id': 'DRONE_MED_1', 'lat_offset': 0.0280, 'lon_offset': 0.0300, 'alt': 330, 'desc': 'Medium risk - near JBU403'},
            {'id': 'DRONE_MED_2', 'lat_offset': -0.0280, 'lon_offset': -0.0300, 'alt': 380, 'desc': 'Medium risk - near SWA504'},
            {'id': 'DRONE_LOW_1', 'lat_offset': 0.0500, 'lon_offset': -0.0080, 'alt': 260, 'desc': 'Low risk'},
            {'id': 'DRONE_LOW_2', 'lat_offset': -0.0120, 'lon_offset': 0.0500, 'alt': 300, 'desc': 'Low risk'},
            {'id': 'DRONE_SAFE_1', 'lat_offset': 0.1000, 'lon_offset': 0.0000, 'alt': 150, 'desc': 'Safe distance'},
            {'id': 'DRONE_SAFE_2', 'lat_offset': 0.0000, 'lon_offset': 0.1000, 'alt': 450, 'desc': 'Safe distance'}
        ]
        
        for i, scenario in enumerate(drone_scenarios):
            drones_data.append({
                'drone_id': scenario['id'],
                'latitude': base_lat + scenario['lat_offset'],
                'longitude': base_lon + scenario['lon_offset'],
                'altitude': scenario['alt'],
                'speed': 15 + (i * 2),
                'heading': i * 40,
                'time_step': 1,
                'timestamp': '2025-10-12 10:00:00'
            })
        
        planes_df = pd.DataFrame(planes_data)
        drones_df = pd.DataFrame(drones_data)
        
        print(f"✓ Created {len(planes_df)} test aircraft and {len(drones_df)} test drones")
        print("Test Aircraft Distribution:")
        print("  - Area: New York City (JFK vicinity)")
        print("  - Altitude range: 200-400m")
        print("  - Expected collision threats: 5-6 alerts")
        
        return planes_df, drones_df
    
    def load_real_data(self):
        """Load real aircraft and drone data (preserving existing logic)."""
        print("Loading real aircraft and drone data from CSV files...")
        
        real_planes_df = pd.DataFrame()
        real_drones_df = pd.DataFrame()
        
        try:
            # Load real plane data
            plane_data_path = "plane_data/opensky_live_states.csv"
            if os.path.exists(plane_data_path):
                real_planes_df = pd.read_csv(plane_data_path)
                print(f"Raw plane data loaded: {len(real_planes_df)} records")
                
                # Clean and filter data
                real_planes_df = real_planes_df.dropna(subset=['latitude', 'longitude', 'icao24', 'baro_altitude'])
                print(f"After removing NaN values: {len(real_planes_df)} records")
                
                # Filter for reasonable altitude range and remove planes on ground
                real_planes_df = real_planes_df[
                    (real_planes_df['baro_altitude'].between(100, 15000)) &
                    (real_planes_df['on_ground'] == False) &
                    (real_planes_df['velocity'] > 50)
                ]
                print(f"After altitude/status filtering: {len(real_planes_df)} records")
                
                # Enhanced regional filtering for richer real mode - targeting 100+ aircraft
                if len(real_planes_df) > 0:
                    # Identify major aviation hubs and regions with optimized sampling for 100+ aircraft
                    regions = [
                        {'name': 'North America', 'lat_min': 25, 'lat_max': 60, 'lon_min': -130, 'lon_max': -60, 'sample_size': 30},
                        {'name': 'Europe', 'lat_min': 35, 'lat_max': 70, 'lon_min': -10, 'lon_max': 30, 'sample_size': 25},
                        {'name': 'Asia-Pacific', 'lat_min': -10, 'lat_max': 50, 'lon_min': 70, 'lon_max': 150, 'sample_size': 25},
                        {'name': 'Middle East', 'lat_min': 15, 'lat_max': 45, 'lon_min': 25, 'lon_max': 70, 'sample_size': 20},
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

            # Load real drone data  
            drone_data_path = "drone_data/dummy_drone_dataset_30.csv"
            if os.path.exists(drone_data_path):
                real_drones_df = pd.read_csv(drone_data_path)
                print(f"Raw drone data loaded: {len(real_drones_df)} records")
                
                # Enhanced drone sampling - get diverse time steps and all drones
                real_drones_df = real_drones_df.dropna(subset=['latitude', 'longitude', 'drone_id', 'altitude'])
                
                unique_drones = real_drones_df['drone_id'].unique()
                selected_drones = []
                
                # Sample multiple time steps for realistic movement
                time_steps = [0, 5, 10, 15, 19]  # Different time points
                for time_step in time_steps:
                    time_data = real_drones_df[real_drones_df['time_step'] == time_step]
                    if not time_data.empty:
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
                
            # Create enhanced realistic collision scenarios with multiple regional hubs
            if len(real_drones_df) > 0 and len(real_planes_df) > 0:
                # Identify drone cluster regions and create aircraft near them
                drone_regions = []
                
                # Group drones by geographic clusters
                lat_groups = real_drones_df.groupby(real_drones_df['latitude'].round(0))
                for lat, lat_group in lat_groups:
                    lon_groups = lat_group.groupby(lat_group['longitude'].round(0))
                    for lon, region_drones in lon_groups:
                        if len(region_drones) >= 2:  # At least 2 drones in region
                            center_lat = region_drones['latitude'].mean()
                            center_lon = region_drones['longitude'].mean()
                            region_name = self.get_region_name(center_lat, center_lon)
                            drone_regions.append({
                                'lat': center_lat,
                                'lon': center_lon,
                                'drone_count': len(region_drones),
                                'region_name': region_name
                            })
                
                print(f"Identified {len(drone_regions)} drone operation regions:")
                
                # Create aircraft near each drone region
                local_aircraft = []
                aircraft_counter = 0
                
                for region in drone_regions:
                    num_aircraft = min(12, region['drone_count'] + 5)  # Enhanced aircraft per region
                    print(f"  {region['region_name']}: {num_aircraft} aircraft near {region['drone_count']} drones")
                    
                    for i in range(num_aircraft):
                        # Use data from existing aircraft but relocate to region
                        base_idx = aircraft_counter % len(real_planes_df)
                        base_aircraft = real_planes_df.iloc[base_idx].copy()
                        
                        # Position aircraft near drone region with enhanced spread
                        lat_offset = (i * 0.002) - 0.01  # Better distribution
                        lon_offset = (i * 0.002) - 0.01
                        
                        base_aircraft['latitude'] = region['lat'] + lat_offset
                        base_aircraft['longitude'] = region['lon'] + lon_offset
                        base_aircraft['icao24'] = f'REG{aircraft_counter:03d}'
                        
                        # Create realistic callsigns based on region
                        callsign = self.generate_regional_callsign(region['region_name'], aircraft_counter)
                        base_aircraft['callsign'] = callsign
                        
                        # Set altitude appropriate for drone interaction (200-800m)
                        base_aircraft['baro_altitude'] = 200 + (i * 60) + random.randint(-40, 40)
                        
                        # Adjust speed for low-altitude operations
                        base_aircraft['velocity'] = 80 + random.randint(20, 70)  # 80-150 m/s
                        
                        local_aircraft.append(base_aircraft)
                        aircraft_counter += 1
                
                if local_aircraft:
                    # Combine global aircraft with regional ones
                    local_aircraft_df = pd.DataFrame(local_aircraft)
                    real_planes_df = pd.concat([real_planes_df, local_aircraft_df], ignore_index=True)
                    print(f"✓ Added {len(local_aircraft)} regional aircraft for enhanced collision scenarios")
                
                print(f"✓ Total aircraft in enriched real scenario: {len(real_planes_df)}")
                
                # Add tight aircraft clusters for better radar visibility
                clustered_aircraft = self.create_tight_aircraft_clusters(real_planes_df, drone_regions)
                if clustered_aircraft:
                    cluster_df = pd.DataFrame(clustered_aircraft)
                    real_planes_df = pd.concat([real_planes_df, cluster_df], ignore_index=True)
                    print(f"✓ Added {len(clustered_aircraft)} tightly clustered aircraft")
                
                # Add enhanced high-altitude aircraft for realistic airspace
                high_altitude_aircraft = []
                for i in range(20):  # Increased from 15 to 20
                    base_aircraft = real_planes_df.iloc[i % min(10, len(real_planes_df))].copy()
                    # Keep original coordinates but ensure high altitude
                    base_aircraft['baro_altitude'] = 8000 + (i * 500)  # 8-18km altitude range
                    base_aircraft['icao24'] = f'HIGH{i:03d}'
                    # Generate high-altitude callsigns
                    ha_callsigns = ['BAW', 'AFR', 'DLH', 'KLM', 'SAS', 'AUA', 'SWR', 'LOT']
                    base_aircraft['callsign'] = f"{ha_callsigns[i % len(ha_callsigns)]}{500 + i}"
                    high_altitude_aircraft.append(base_aircraft)
                
                if high_altitude_aircraft:
                    high_alt_df = pd.DataFrame(high_altitude_aircraft)
                    real_planes_df = pd.concat([real_planes_df, high_alt_df], ignore_index=True)
                    print(f"✓ Added {len(high_altitude_aircraft)} high-altitude aircraft for realism")
                
        except Exception as e:
            print(f"Error loading real data: {e}")
            real_planes_df = pd.DataFrame()
            real_drones_df = pd.DataFrame()
            
        return real_planes_df, real_drones_df
    
    def create_tight_aircraft_clusters(self, base_aircraft_df, drone_regions):
        """Create tight clusters of aircraft around major drone operation areas for better radar visibility."""
        if base_aircraft_df.empty or not drone_regions:
            return []
            
        cluster_aircraft = []
        
        # Create clusters around each drone region
        for region_idx, region in enumerate(drone_regions):
            drone_center_lat = region['lat']
            drone_center_lon = region['lon']
        
            print(f"Creating tight aircraft clusters around {region['region_name']}: ({drone_center_lat:.3f}, {drone_center_lon:.3f})")
            
            existing_count = len(base_aircraft_df)
            
            # Create concentric rings of aircraft around drone operations (like test mode)
            for ring in range(1, 4):  # 3 rings per region
                ring_distance = ring * 0.01  # 0.01, 0.02, 0.03 degrees (~1-3 km)
                aircraft_in_ring = 8 if ring == 1 else 6 if ring == 2 else 4  # More in inner rings
                
                for i in range(aircraft_in_ring):
                    angle = (360 / aircraft_in_ring) * i
                    import math
                    angle_rad = math.radians(angle)
                    
                    # Calculate position in the ring
                    new_lat = drone_center_lat + (ring_distance * math.cos(angle_rad))
                    new_lon = drone_center_lon + (ring_distance * math.sin(angle_rad))
                    
                    # Use existing aircraft as template but change position
                    template_idx = (region_idx * 50 + ring * 10 + i) % min(20, existing_count)
                    if template_idx < len(base_aircraft_df):
                        template_aircraft = base_aircraft_df.iloc[template_idx].copy()
                        
                        # Modify the template for tight clustering
                        template_aircraft['latitude'] = new_lat
                        template_aircraft['longitude'] = new_lon
                        template_aircraft['icao24'] = f'CLU{region_idx}{ring}{i:02d}'
                        template_aircraft['callsign'] = self.generate_regional_callsign(region['region_name'], region_idx * 50 + ring * 10 + i)
                        template_aircraft['baro_altitude'] = 200 + (ring * 80) + (i * 15)  # Varied altitudes
                        template_aircraft['velocity'] = 80 + (i * 5) + random.randint(-10, 10)
                        template_aircraft['true_track'] = (angle + 90) % 360  # Realistic headings
                    
                        cluster_aircraft.append(template_aircraft)
        
        return cluster_aircraft

    def load_all_data(self):
        """Load both test and real data, then set current data based on mode."""
        print("Initializing SkyLink Unified System Data...")
        
        # Load test scenario
        self.test_planes_df, self.test_drones_df = self.create_test_collision_scenario()
        
        # Load real data (clustering now done inside load_real_data)
        self.real_planes_df, self.real_drones_df = self.load_real_data()
        
        # Set current data based on mode
        self.switch_data_mode()
        
        print(f"✓ Switched to {'TEST' if self.use_test_data else 'REAL'} MODE: {len(self.planes_df)} planes, {len(self.drones_df)} drones")
    
    def switch_data_mode(self):
        """Switch between test and real data modes with enhanced real mode targeting 100+ aircraft and 30 drones."""
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
                # Prefer clustered aircraft (CLU prefix) for better local clustering
                clustered_aircraft = self.planes_df[self.planes_df['icao24'].str.startswith('CLU', na=False)]
                regional_aircraft = self.planes_df[self.planes_df['icao24'].str.startswith('REG', na=False)]
                
                if not clustered_aircraft.empty:
                    self.current_aircraft_callsign = str(clustered_aircraft.iloc[0]['callsign']).strip()
                    print(f"✓ Selected clustered aircraft: {self.current_aircraft_callsign}")
                elif not regional_aircraft.empty:
                    self.current_aircraft_callsign = str(regional_aircraft.iloc[0]['callsign']).strip()
                    print(f"✓ Selected regional aircraft: {self.current_aircraft_callsign}")
                else:
                    self.current_aircraft_callsign = str(self.planes_df.iloc[0]['callsign']).strip()
                    print(f"✓ Selected aircraft: {self.current_aircraft_callsign}")
                    
            print(f"✓ Switched to REAL DATA MODE: {len(self.planes_df)} planes, {len(self.drones_df)} drones")
    
    # Include all existing pilot dashboard methods (preserving logic)
    def get_current_aircraft(self, callsign: str = None) -> Optional[Dict]:
        """Get current aircraft data (preserving existing logic)."""
        if callsign:
            self.current_aircraft_callsign = callsign
            
        if self.planes_df.empty:
            return None
        
        if not self.current_aircraft_callsign:
            if self.use_test_data:
                self.current_aircraft_callsign = "UAL100"
            else:
                # For real data, use first Bangalore aircraft (AI100, AI101, AI102)
                bangalore_aircraft = self.planes_df[self.planes_df['callsign'].str.contains('AI1', na=False)]
                if not bangalore_aircraft.empty:
                    self.current_aircraft_callsign = bangalore_aircraft.iloc[0]['callsign'].strip()
                else:
                    self.current_aircraft_callsign = self.planes_df.iloc[0]['callsign'].strip()
            
        current_plane = self.planes_df[
            self.planes_df['callsign'].str.strip() == self.current_aircraft_callsign
        ]
        
        if current_plane.empty:
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
    
    def get_nearby_aircraft(self, current_aircraft: Dict, radar_range_nm: float = 10) -> List[Dict]:
        """Get aircraft within radar range of current aircraft with smart proximity filtering."""
        try:
            if not current_aircraft or self.planes_df.empty:
                return []
            
            current_lat = current_aircraft['latitude']
            current_lon = current_aircraft['longitude']
            current_alt = current_aircraft['altitude']
            current_callsign = current_aircraft['callsign']
            
            print(f"Looking for aircraft near {current_callsign} at ({current_lat:.4f}, {current_lon:.4f})")
            print(f"Total aircraft in database: {len(self.planes_df)}")
            
            # Collect all aircraft with distances
            all_aircraft_with_distance = []
            
            for _, plane in self.planes_df.iterrows():
                # Skip current aircraft
                try:
                    if plane['callsign'].strip() == current_callsign:
                        continue
                        
                    plane_lat = float(plane.get('latitude', 0))
                    plane_lon = float(plane.get('longitude', 0))
                    plane_alt = float(plane.get('baro_altitude', 0))
                    
                    # Skip planes with invalid coordinates
                    if plane_lat == 0 and plane_lon == 0:
                        continue
                    
                    # Calculate distance
                    distance_km = calculate_horizontal_distance(current_lat, current_lon, plane_lat, plane_lon)
                    distance_nm = distance_km / 1.852
                    
                    aircraft_info = {
                        'callsign': plane.get('callsign', '').strip(),
                        'icao24': plane.get('icao24', ''),
                        'latitude': plane_lat,
                        'longitude': plane_lon,
                        'altitude': plane_alt,
                        'speed': float(plane.get('velocity', 0)),
                        'heading': float(plane.get('true_track', 0)) if pd.notna(plane.get('true_track')) else 0.0,
                        'distance_nm': distance_nm,
                        'relative_altitude': plane_alt - current_alt,
                        'country': plane.get('origin_country', 'Unknown')
                    }
                    
                    all_aircraft_with_distance.append((aircraft_info, distance_nm))
                        
                except (ValueError, TypeError, AttributeError) as e:
                    print(f"Error processing aircraft {plane.get('callsign', 'Unknown')}: {e}")
                    continue
            
            # Sort all aircraft by distance
            all_aircraft_with_distance.sort(key=lambda x: x[1])
            
            if not self.use_test_data:
                # REAL MODE: Use smart proximity approach - take closest aircraft
                target_count = min(50, len(all_aircraft_with_distance))  # Reduced from 100 to 50 for stability
                nearby_aircraft = [aircraft for aircraft, _ in all_aircraft_with_distance[:target_count]]
                print(f"REAL MODE: Selected {len(nearby_aircraft)} closest aircraft")
                if nearby_aircraft:
                    print(f"  Closest: {nearby_aircraft[0]['callsign']} at {nearby_aircraft[0]['distance_nm']:.1f} NM")
                    if len(nearby_aircraft) > 1:
                        print(f"  Farthest: {nearby_aircraft[-1]['callsign']} at {nearby_aircraft[-1]['distance_nm']:.1f} NM")
            else:
                # TEST MODE: Use fixed radar range
                nearby_aircraft = [aircraft for aircraft, distance in all_aircraft_with_distance if distance <= radar_range_nm]
                print(f"TEST MODE: Found {len(nearby_aircraft)} aircraft within {radar_range_nm} NM")
            
            return nearby_aircraft
            
        except Exception as e:
            print(f"Error in get_nearby_aircraft: {e}")
            return []
        
    def get_nearby_drones(self, current_aircraft: Dict, range_nm: float = 10) -> List[Dict]:
        """Get nearby drones within specified range."""
        if self.drones_df.empty or not current_aircraft:
            return []
            
        nearby_drones = []
        current_lat = current_aircraft['latitude']
        current_lon = current_aircraft['longitude']
        
        # Enhanced range for real mode to show more drones
        effective_range = range_nm * 2 if not self.use_test_data else range_nm
        
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
        
        # Return more drones in real mode for enriched experience
        max_drones = 30 if not self.use_test_data else 15
        return nearby_drones[:max_drones]
    
    def get_all_drones_for_display(self) -> List[Dict]:
        """Get all drones for map display."""
        if self.drones_df.empty:
            return []
        
        drones = []
        for _, drone in self.drones_df.iterrows():
            try:
                drones.append({
                    'drone_id': drone.get('drone_id', ''),
                    'latitude': float(drone.get('latitude', 0)),
                    'longitude': float(drone.get('longitude', 0)),
                    'altitude': float(drone.get('altitude', 0)),
                    'speed': float(drone.get('speed', 0)),
                    'heading': float(drone.get('heading', 0)) if pd.notna(drone.get('heading')) else 0.0,
                })
            except (ValueError, TypeError):
                continue
        
        return drones
    
    def calculate_bearing(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate bearing from point 1 to point 2."""
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
    
    def calculate_bearing(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate bearing from point 1 to point 2."""
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
    
    def get_collision_alerts_for_all(self):
        """Generate collision alerts for all aircraft and drones."""
        if self.planes_df.empty or self.drones_df.empty:
            return []
            
        alerts = detect_collisions(
            self.planes_df, 
            self.drones_df, 
            h_threshold=0.5, 
            v_threshold=100
        )
        
        return alerts
    
    def get_system_status(self):
        """Get overall system status for the main dashboard."""
        total_aircraft = len(self.planes_df) if not self.planes_df.empty else 0
        total_drones = len(self.drones_df) if not self.drones_df.empty else 0
        total_alerts = len(self.get_collision_alerts_for_all())
        
        return {
            'aircraft_count': total_aircraft,
            'drone_count': total_drones,
            'alert_count': total_alerts,
            'data_mode': 'TEST SCENARIO' if self.use_test_data else 'REAL DATA',
            'system_status': 'OPERATIONAL' if total_aircraft > 0 and total_drones > 0 else 'LIMITED DATA',
            'last_update': datetime.now().isoformat()
        }

# Initialize unified service
skylink_service = SkyLinkUnifiedService()

# Routes
@app.route('/')
def index():
    """Main hub page with access to both dashboards."""
    return render_template('index.html')

@app.route('/pilot-dashboard')
def pilot_dashboard():
    """Pilot cockpit dashboard - uses the main templates folder for both test and real modes."""
    return render_template('pilot_dashboard.html')

@app.route('/drone-dashboard')
def drone_dashboard():
    """Drone operator dashboard - using the exact same design as drone_dashboard_demo."""
    try:
        # Prepare data for the dashboard
        drone_data = []
        plane_data = []
        
        # Convert DataFrame to list of dictionaries for the dashboard
        if not skylink_service.drones_df.empty:
            for _, row in skylink_service.drones_df.iterrows():
                drone_dict = {
                    'drone_id': row.get('drone_id', f"drone_{_}"),
                    'latitude': float(row.get('latitude', 0)),
                    'longitude': float(row.get('longitude', 0)),
                    'altitude': float(row.get('altitude', 0)),
                    'speed': float(row.get('speed', 0)),
                    'heading': float(row.get('heading', 0)),
                    'timestamp': row.get('timestamp', datetime.now().isoformat())
                }
                drone_data.append(drone_dict)
        
        # Convert plane data
        if not skylink_service.planes_df.empty:
            for _, row in skylink_service.planes_df.iterrows():
                if pd.isna(row.get('latitude')) or pd.isna(row.get('longitude')):
                    continue
                    
                plane_dict = {
                    'callsign': str(row.get('callsign', f"aircraft_{_}")).strip(),
                    'icao24': row.get('icao24', f"unknown_{_}"),
                    'latitude': float(row.get('latitude', 0)),
                    'longitude': float(row.get('longitude', 0)),
                    'altitude': float(row.get('baro_altitude', 0)) if not pd.isna(row.get('baro_altitude')) else 0,
                    'velocity': float(row.get('velocity', 0)) if not pd.isna(row.get('velocity')) else 0,
                    'heading': float(row.get('true_track', 0)) if not pd.isna(row.get('true_track')) else 0,
                    'timestamp': row.get('time_position', datetime.now().timestamp())
                }
                plane_data.append(plane_dict)
        
        # Generate dashboard HTML using the DroneDashboard class
        dashboard = skylink_service.drone_dashboard
        all_alerts = dashboard.alert_translator.process_multiple_alerts(drone_data, plane_data)
        dashboard_html = dashboard._create_dashboard_html(all_alerts, drone_data)
        
        # Return the generated HTML directly
        return Response(dashboard_html, mimetype='text/html')
        
    except Exception as e:
        print(f"Error generating drone dashboard: {e}")
        import traceback
        traceback.print_exc()
        return render_template('drone_dashboard.html')  # Fallback to template

# API Routes (preserving existing logic)
@app.route('/api/system-status')
def get_system_status():
    """Get overall system status."""
    try:
        status = skylink_service.get_system_status()
        return jsonify(status)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/toggle-data-source', methods=['POST'])
def toggle_data_source():
    """Toggle between test and real data."""
    try:
        skylink_service.use_test_data = not skylink_service.use_test_data
        skylink_service.switch_data_mode()
        
        return jsonify({
            'success': True,
            'data_source': 'TEST SCENARIO' if skylink_service.use_test_data else 'REAL DATA',
            'using_test_data': skylink_service.use_test_data,
            'planes_loaded': len(skylink_service.planes_df),
            'drones_loaded': len(skylink_service.drones_df)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/pilot-data')
def get_pilot_data():
    """API endpoint for pilot dashboard (preserving existing logic)."""
    try:
        callsign = request.args.get('callsign', skylink_service.current_aircraft_callsign)
        radar_range = float(request.args.get('range', 10))
        
        current_aircraft = skylink_service.get_current_aircraft(callsign)
        
        if not current_aircraft:
            return jsonify({
                'error': 'Aircraft not found',
                'current_aircraft': None,
                'nearby_aircraft': [],
                'all_drones': [],
                'threats': []
            })
        
        # Get nearby aircraft within radar range
        nearby_aircraft = skylink_service.get_nearby_aircraft(current_aircraft, radar_range)
        
        # Get nearby drones within radar range
        nearby_drones = skylink_service.get_nearby_drones(current_aircraft, radar_range)
        
        # Get all drones for map display
        all_drones = skylink_service.get_all_drones_for_display()
        
        # Get collision threats for current aircraft
        threats = skylink_service.get_collision_alerts_for_all()
        
        # Filter threats relevant to current aircraft
        relevant_threats = [
            threat for threat in threats 
            if threat.get('plane_icao24') == current_aircraft.get('icao24')
        ]
        
        return jsonify({
            'current_aircraft': current_aircraft,
            'nearby_aircraft': nearby_aircraft,
            'nearby_drones': nearby_drones,
            'all_drones': all_drones,
            'threats': relevant_threats,
            'timestamp': datetime.now().isoformat(),
            'radar_range_nm': radar_range,
            'data_source': "test_scenario" if skylink_service.use_test_data else "real_data",
            'total_aircraft': len(skylink_service.planes_df),
            'total_drones': len(skylink_service.drones_df)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/drone-data')
def get_drone_data():
    """API endpoint for drone dashboard."""
    try:
        # Prepare data in the same format as drone_dashboard_demo
        drone_data = []
        plane_data = []
        
        # Convert DataFrame to list of dictionaries for the dashboard
        if not skylink_service.drones_df.empty:
            for _, row in skylink_service.drones_df.iterrows():
                drone_dict = {
                    'drone_id': row.get('drone_id', f"drone_{_}"),
                    'latitude': float(row.get('latitude', 0)),
                    'longitude': float(row.get('longitude', 0)),
                    'altitude': float(row.get('altitude', 0)),
                    'speed': float(row.get('speed', 0)),
                    'heading': float(row.get('heading', 0)),
                    'timestamp': row.get('timestamp', datetime.now().isoformat())
                }
                drone_data.append(drone_dict)
        
        # Convert plane data
        if not skylink_service.planes_df.empty:
            for _, row in skylink_service.planes_df.iterrows():
                if pd.isna(row.get('latitude')) or pd.isna(row.get('longitude')):
                    continue
                    
                plane_dict = {
                    'callsign': str(row.get('callsign', f"aircraft_{_}")).strip(),
                    'icao24': row.get('icao24', f"unknown_{_}"),
                    'latitude': float(row.get('latitude', 0)),
                    'longitude': float(row.get('longitude', 0)),
                    'altitude': float(row.get('baro_altitude', 0)) if not pd.isna(row.get('baro_altitude')) else 0,
                    'velocity': float(row.get('velocity', 0)) if not pd.isna(row.get('velocity')) else 0,
                    'heading': float(row.get('true_track', 0)) if not pd.isna(row.get('true_track')) else 0,
                    'timestamp': row.get('time_position', datetime.now().timestamp())
                }
                plane_data.append(plane_dict)
        
        # Process alerts using the alert translator (same as demo)
        all_alerts = skylink_service.drone_dashboard.alert_translator.process_multiple_alerts(drone_data, plane_data)
        
        return jsonify({
            'drone_data': drone_data,
            'plane_data': plane_data,
            'all_alerts': all_alerts,
            'timestamp': datetime.now().isoformat(),
            'system_status': skylink_service.get_system_status()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500



# At the very end of the file, replace the existing if __name__ == '__main__': section:

if __name__ == '__main__':
    # Get configuration from environment variables with proper defaults for Render
    host = os.environ.get('HOST', '0.0.0.0')
    port = int(os.environ.get('PORT', 10000))  # Render uses port 10000 by default
    flask_env = os.environ.get('FLASK_ENV', 'production')
    debug = flask_env == 'development'
    
    print("🚁✈️ Starting SkyLink Unified System...")
    print("="*60)
    print(f"Environment: {flask_env}")
    print(f"Host: {host}")
    print(f"Port: {port}")
    print(f"Debug: {debug}")
    
    if debug:
        print("Available Interfaces:")
        print(f"  🏠 Main Hub: http://localhost:{port}")
        print(f"  ✈️  Pilot Dashboard: http://localhost:{port}/pilot-dashboard")  
        print(f"  🚁 Drone Dashboard: http://localhost:{port}/drone-dashboard")
    else:
        print("🌐 Running in production mode")
        print(f"  🌐 Application running on port {port}")
    print("="*60)
    
    app.run(debug=debug, host=host, port=port)