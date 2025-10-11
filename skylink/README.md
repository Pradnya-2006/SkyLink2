# SkyLink - Real-time Drone and Plane Collision Detection System

A Python-based system for detecting potential collisions between drones and aircraft using real-time position data and interactive visualization.

## 🚀 Features

- **Real-time Collision Detection**: Monitors horizontal and vertical distances between drones and planes
- **Interactive Visualization**: Folium-based maps showing aircraft positions and collision alerts
- **Configurable Thresholds**: Customizable distance thresholds for collision detection
- **Multiple Output Formats**: Saves alerts in JSON and CSV formats
- **Comprehensive Reporting**: Detailed summary statistics and analysis

## 📁 Project Structure

```
skylink/
├── plane_data/
│   └── opensky_live_states.csv          # Aircraft position data
├── drone_data/
│   └── dummy_drone_dataset_30.csv       # Drone position data
├── collision_module/
│   ├── __init__.py                      # Package initialization
│   └── collision_detection.py          # Core collision detection logic
├── outputs/                             # Generated output files
├── visualization.py                     # Map visualization functions
├── main.py                             # Main application workflow
├── requirements.txt                     # Python dependencies
└── README.md                           # This file
```

## 🔧 Installation

1. **Clone or download the project**
2. **Install Python 3.12+**
3. **Install required dependencies:**

```bash
pip install -r requirements.txt
```

## 📊 Data Format

### Plane Data (opensky_live_states.csv)
Required columns:
- `icao24`: Aircraft ICAO 24-bit identifier
- `callsign`: Aircraft callsign
- `latitude`: Aircraft latitude (decimal degrees)
- `longitude`: Aircraft longitude (decimal degrees)
- `baro_altitude`: Barometric altitude (meters)
- `velocity`: Ground velocity (m/s)

### Drone Data (dummy_drone_dataset_30.csv)
Required columns:
- `time_step`: Time step identifier
- `drone_id`: Unique drone identifier
- `latitude`: Drone latitude (decimal degrees)
- `longitude`: Drone longitude (decimal degrees)
- `altitude`: Drone altitude (meters)
- `speed`: Drone speed (m/s)
- `heading`: Drone heading (degrees)
- `timestamp`: Timestamp of the record

## 🎯 Usage

### Basic Usage

```bash
cd skylink
python main.py
```

### Advanced Usage

```python
from collision_module.collision_detection import detect_collisions
from visualization import plot_airspace
import pandas as pd

# Load your data
planes_df = pd.read_csv('plane_data/opensky_live_states.csv')
drones_df = pd.read_csv('drone_data/dummy_drone_dataset_30.csv')

# Detect collisions with custom thresholds
alerts = detect_collisions(
    planes_df, 
    drones_df, 
    h_threshold=0.3,  # 300m horizontal
    v_threshold=50    # 50m vertical
)

# Create visualization
plot_airspace(planes_df, drones_df, alerts, 'my_map.html')
```

## ⚙️ Configuration

### Collision Detection Thresholds

- **Horizontal Threshold**: Default 0.5 km (configurable)
- **Vertical Threshold**: Default 100 meters (configurable)

### Output Files

The system generates several output files:

1. **JSON Alerts**: `outputs/collision_alerts_TIMESTAMP.json`
2. **CSV Alerts**: `outputs/collision_alerts_TIMESTAMP.csv`
3. **Airspace Map**: `outputs/airspace_map_TIMESTAMP.html`
4. **Summary Map**: `outputs/alerts_summary_TIMESTAMP.html` (if alerts exist)

## 🗺️ Visualization

### Map Features

- **Blue Circles**: Aircraft/Planes
- **Green Circles**: Drones
- **Red Circles**: Collision alerts
- **Dashed Red Lines**: Connect conflicting aircraft
- **Interactive Popups**: Detailed information for each object
- **Multiple Layers**: Different map tile options
- **Legend**: Clear identification of map elements

## 📈 Output Analysis

### Alert Information
Each collision alert contains:
- Drone ID and Plane ICAO24 identifier
- Horizontal distance (kilometers)
- Vertical distance (meters)
- Position coordinates for both aircraft
- Altitude information
- Additional metadata (callsign, speed, etc.)

### Summary Statistics
- Total number of alerts
- Unique aircraft involved
- Distance statistics (min, max, average)
- Risk level categorization

## 🔍 API Reference

### Core Functions

#### `detect_collisions(planes_df, drones_df, h_threshold=0.5, v_threshold=100)`
Detect potential collisions between aircraft.

**Parameters:**
- `planes_df`: DataFrame with plane data
- `drones_df`: DataFrame with drone data
- `h_threshold`: Horizontal distance threshold (km)
- `v_threshold`: Vertical distance threshold (m)

**Returns:** List of collision alert dictionaries

#### `plot_airspace(planes_df, drones_df, alerts, map_file="outputs/airspace_map.html")`
Create interactive map visualization.

**Parameters:**
- `planes_df`: DataFrame with plane data
- `drones_df`: DataFrame with drone data
- `alerts`: List of collision alerts
- `map_file`: Output HTML file path

**Returns:** Boolean success indicator

## 🚨 Error Handling

The system includes comprehensive error handling for:
- Missing or corrupted data files
- Invalid coordinate data
- Network connectivity issues
- File I/O errors
- Data format inconsistencies

## 🧪 Testing

Run the system with sample data to verify functionality:

```bash
# Ensure your CSV files are in the correct directories
python main.py
```

Check the `outputs/` folder for generated files.

## 📋 Requirements

- Python 3.12+
- pandas >= 2.0.0
- numpy >= 1.24.0
- folium >= 0.14.0
- geopy >= 2.3.0

## 🔧 Troubleshooting

### Common Issues

1. **FileNotFoundError**: Ensure CSV files are in correct directories
2. **Empty datasets**: Check data file format and content
3. **Map not displaying**: Verify output directory permissions
4. **Distance calculations**: Ensure coordinate data is valid

### Performance Tips

- Filter data by geographic region for large datasets
- Adjust thresholds based on airspace density
- Use time-windowed analysis for real-time processing

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is provided as-is for educational and research purposes.

## 📞 Support

For issues and questions:
1. Check this README
2. Review error messages carefully
3. Verify data file formats
4. Test with sample data

---

**SkyLink** - Keeping our skies safe through intelligent collision detection! ✈️🚁