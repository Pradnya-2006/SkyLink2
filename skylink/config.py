"""
SkyLink Configuration Settings

This module contains configuration parameters for the SkyLink collision detection system.
Modify these settings to customize system behavior.
"""

import os

# ============================================================================
# COLLISION DETECTION SETTINGS
# ============================================================================

# Distance thresholds for collision detection
HORIZONTAL_THRESHOLD_KM = 0.5    # Horizontal separation threshold in kilometers
VERTICAL_THRESHOLD_M = 100       # Vertical separation threshold in meters

# Advanced thresholds for different risk levels
RISK_THRESHOLDS = {
    'critical': {'horizontal_km': 0.1, 'vertical_m': 30},
    'high': {'horizontal_km': 0.2, 'vertical_m': 50},
    'medium': {'horizontal_km': 0.3, 'vertical_m': 75},
    'low': {'horizontal_km': 0.5, 'vertical_m': 100}
}

# ============================================================================
# DATA PROCESSING SETTINGS
# ============================================================================

# File paths
PLANE_DATA_PATH = "plane_data/opensky_live_states.csv"
DRONE_DATA_PATH = "drone_data/dummy_drone_dataset_30.csv"
OUTPUT_DIRECTORY = "outputs"

# Data validation settings
REQUIRED_PLANE_COLUMNS = ['icao24', 'latitude', 'longitude', 'baro_altitude']
REQUIRED_DRONE_COLUMNS = ['drone_id', 'latitude', 'longitude', 'altitude']

# Data filtering options
ALTITUDE_FILTER_ENABLED = False
MAX_ALTITUDE_M = 1000              # Maximum altitude to consider (if filter enabled)
MIN_ALTITUDE_M = 0                 # Minimum altitude to consider (if filter enabled)

GEOGRAPHIC_FILTER_ENABLED = False
# Define bounding box for geographic filtering (if enabled)
GEO_BOUNDS = {
    'min_lat': 40.0,
    'max_lat': 41.0,
    'min_lon': -75.0,
    'max_lon': -73.0
}

# ============================================================================
# VISUALIZATION SETTINGS
# ============================================================================

# Map settings
DEFAULT_ZOOM_LEVEL = 8
MAP_TILES = 'OpenStreetMap'        # Options: 'OpenStreetMap', 'CartoDB positron', etc.

# Marker settings
PLANE_MARKER_CONFIG = {
    'radius': 8,
    'color': 'blue',
    'fillColor': 'lightblue',
    'fillOpacity': 0.7,
    'weight': 2
}

DRONE_MARKER_CONFIG = {
    'radius': 6,
    'color': 'green',
    'fillColor': 'lightgreen',
    'fillOpacity': 0.7,
    'weight': 2
}

ALERT_MARKER_CONFIG = {
    'radius': 12,
    'color': 'red',
    'fillColor': 'red',
    'fillOpacity': 0.8,
    'weight': 3
}

# Alert visualization settings
SHOW_ALERT_CONNECTIONS = True      # Draw lines between conflicting aircraft
CONNECTION_LINE_CONFIG = {
    'color': 'red',
    'weight': 2,
    'opacity': 0.6,
    'dash_array': '5, 10'
}

# ============================================================================
# OUTPUT SETTINGS
# ============================================================================

# File naming
USE_TIMESTAMP_IN_FILENAMES = True
TIMESTAMP_FORMAT = "%Y%m%d_%H%M%S"

# Output file formats
SAVE_JSON_ALERTS = True
SAVE_CSV_ALERTS = True
CREATE_MAIN_MAP = True
CREATE_SUMMARY_MAP = True

# JSON output options
JSON_INDENT = 2
JSON_ENSURE_ASCII = False

# ============================================================================
# PERFORMANCE SETTINGS
# ============================================================================

# Processing options
ENABLE_PARALLEL_PROCESSING = False  # Enable multiprocessing (experimental)
MAX_WORKER_THREADS = 4              # Number of worker threads (if parallel processing enabled)

# Memory management
MAX_RECORDS_PER_BATCH = 10000       # Process data in batches for large datasets
ENABLE_BATCH_PROCESSING = False     # Enable batch processing for large datasets

# ============================================================================
# LOGGING SETTINGS
# ============================================================================

# Console output
VERBOSE_OUTPUT = True               # Enable detailed console output
SHOW_PROGRESS_BARS = False         # Show progress bars for long operations (requires tqdm)

# Status reporting
REPORT_PROCESSING_STATS = True      # Show processing statistics
REPORT_TIMING_INFO = True          # Show execution timing information

# ============================================================================
# SYSTEM SETTINGS
# ============================================================================

# Version information
VERSION = "1.0.0"
SYSTEM_NAME = "SkyLink Collision Detection System"

# Error handling
CONTINUE_ON_DATA_ERRORS = True      # Continue processing if some records have errors
STRICT_COLUMN_VALIDATION = False   # Require all expected columns to be present

# Compatibility options
PANDAS_ENGINE = 'python'           # CSV reading engine: 'c', 'python', or 'pyarrow'
DATE_FORMAT = 'ISO8601'           # Date format for timestamps

# ============================================================================
# DEPLOYMENT CONFIGURATION
# ============================================================================

class FlaskConfig:
    """Base Flask configuration"""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'skylink-development-key-2024')
    
class DevelopmentConfig(FlaskConfig):
    """Development configuration"""
    DEBUG = True
    HOST = '0.0.0.0'
    PORT = 5000
    
class ProductionConfig(FlaskConfig):
    """Production configuration"""
    DEBUG = False
    HOST = '0.0.0.0'
    PORT = int(os.environ.get('PORT', 8080))
    SECRET_KEY = os.environ.get('SECRET_KEY')  # Must be set in production

# Select configuration based on environment
FLASK_CONFIGS = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

def get_flask_config():
    """Get Flask configuration based on FLASK_ENV"""
    import os
    env = os.environ.get('FLASK_ENV', 'development')
    return FLASK_CONFIGS.get(env, FLASK_CONFIGS['default'])