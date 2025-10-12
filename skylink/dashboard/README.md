# SkyLink Pilot Dashboard

A real-time cockpit-style dashboard for pilots with collision detection, voice alerts, and interactive mapping.

## 🎛️ Features

### Cockpit Interface
- **Real-time Aircraft Display**: Shows current aircraft position, altitude, speed, and heading
- **Radar-style Map**: Interactive map with aircraft and drone positions
- **Threat Assessment Panel**: Real-time collision alerts with risk levels
- **Status Indicators**: Navigation, communication, and traffic alert system status
- **Voice Alerts**: Text-to-speech collision warnings

### Safety Features
- **Multi-level Threat Detection**:
  - **Critical**: < 0.1km horizontal, < 30m vertical
  - **High**: < 0.3km horizontal, < 50m vertical  
  - **Medium**: < 0.5km horizontal, < 100m vertical
  - **Low**: < 1.0km horizontal, < 150m vertical
- **Nearby Traffic Display**: Shows all aircraft within radar range
- **Audio Warnings**: Voice alerts for collision threats
- **Emergency Button**: Quick emergency declaration

### Controls
- **Voice Toggle**: Enable/disable audio alerts
- **Auto Update**: Real-time data refresh (2-second intervals)
- **Radar Range**: Adjustable radar range (10, 20, 50 NM)
- **Aircraft Selection**: Choose which aircraft to pilot

## 🚀 Quick Start

### Method 1: Batch File (Windows)
```batch
# Double-click to run
start_dashboard.bat
```

### Method 2: Python Script
```bash
cd dashboard
python launch_dashboard.py
```

### Method 3: Direct Flask
```bash
cd dashboard
python app.py
```

## 🌐 Access Dashboard

Once started, open your browser to:
```
http://localhost:5000
```

## 📊 Dashboard Layout

```
┌─────────────────────────────────────────────────────────────┐
│                    AIRCRAFT INFO & STATUS                   │
├─────────────┬───────────────────────────────┬─────────────────┤
│  AIRCRAFT   │                               │   COLLISION     │
│   STATUS    │           RADAR MAP           │    ALERTS       │
│             │                               │                 │
│  • Position │    • Current Aircraft         │  • Critical     │
│  • Speed    │    • Nearby Traffic          │  • High Risk    │
│  • Altitude │    • Drones                   │  • Medium       │
│  • Heading  │    • Threats                  │  • Low Risk     │
│             │    • Range Circles            │                 │
├─────────────┴───────────────────────────────┴─────────────────┤
│                       CONTROLS                                │
│     [Voice]    [Auto Update]    [Range]    [Emergency]       │
└─────────────────────────────────────────────────────────────┘
```

## 🎮 Controls & Interface

### Status Panel (Left)
- **Aircraft Position**: Live GPS coordinates
- **Flight Parameters**: Speed, altitude, heading, vertical rate
- **Nearby Traffic**: List of aircraft within radar range

### Radar Map (Center)
- **Blue Aircraft Icons**: Your aircraft and nearby traffic
- **Orange Helicopter Icons**: Drones
- **Red Warning Icons**: Collision threats
- **Green Radar Circle**: Current radar range
- **Interactive Popups**: Click objects for details

### Threat Panel (Right)
- **Color-coded Alerts**: Critical (red), High (orange), Medium (yellow), Low (cyan)
- **Distance Information**: Horizontal and vertical separation
- **Risk Assessment**: Real-time threat level updates
- **Clear Status**: "Airspace Clear" when no threats detected

### Control Panel (Bottom)
- **Voice Alerts**: Toggle audio collision warnings
- **Auto Update**: Enable/disable real-time data refresh
- **Radar Range**: Switch between 10, 20, 50 nautical miles
- **Emergency**: Declare emergency with voice announcement

## 🔊 Voice Alerts

The system provides audio warnings for collision threats:

- **Critical Threats**: "Traffic alert! Critical threat from drone DRONE_ID at distance X kilometers"
- **High Threats**: "Traffic advisory. Drone DRONE_ID at distance X kilometers"
- **System Status**: "Voice alerts enabled/disabled"
- **Emergency**: "Mayday, mayday, mayday"

## 📡 API Endpoints

### Get Pilot Data
```
GET /api/pilot-data?callsign=AI101&range=10
```
Returns current aircraft position, nearby traffic, and collision threats.

### Get Aircraft List
```
GET /api/aircraft-list
```
Returns list of available aircraft callsigns.

### Set Current Aircraft
```
POST /api/set-aircraft
Content-Type: application/json

{
  "callsign": "AI101"
}
```

### Reload Data
```
POST /api/reload-data
```
Reloads aircraft and drone data from CSV files.

## 🛠️ Configuration

### Data Sources
- **Aircraft Data**: `../plane_data/opensky_live_states.csv`
- **Drone Data**: `../drone_data/dummy_drone_dataset_30.csv`

### Default Settings
- **Update Interval**: 2 seconds
- **Default Radar Range**: 10 nautical miles
- **Default Aircraft**: First aircraft in dataset
- **Voice Alerts**: Enabled by default

### Threat Thresholds
```python
threat_levels = [
    {'name': 'critical', 'h_threshold': 0.1, 'v_threshold': 30},
    {'name': 'high', 'h_threshold': 0.3, 'v_threshold': 50},
    {'name': 'medium', 'h_threshold': 0.5, 'v_threshold': 100},
    {'name': 'low', 'h_threshold': 1.0, 'v_threshold': 150}
]
```

## 🔧 Technical Requirements

### Dependencies
```
flask>=2.3.0
pandas>=2.0.0
numpy>=1.24.0
geopy>=2.3.0
```

### Browser Compatibility
- **Chrome/Edge**: Full support including voice synthesis
- **Firefox**: Full support including voice synthesis  
- **Safari**: Full support including voice synthesis
- **Mobile**: Responsive design, limited voice support

### System Requirements
- **Python**: 3.8+
- **RAM**: 512MB minimum
- **Network**: None required (uses local data files)

## 🚨 Emergency Procedures

### Collision Alert Response
1. **Visual Alert**: Red banner appears with threat information
2. **Audio Alert**: Voice warning with threat details
3. **Manual Action**: Pilot should take evasive action
4. **Emergency Declaration**: Use emergency button if needed

### System Failure
1. **Data Loss**: Dashboard shows "Loading..." status
2. **Connection Issues**: Check Flask server console
3. **Browser Issues**: Refresh page or try different browser

## 📋 Troubleshooting

### Common Issues

**Dashboard not loading**
- Check that Flask server is running on port 5000
- Verify data files exist in correct locations
- Check browser console for JavaScript errors

**No aircraft data**
- Ensure CSV files are in correct directories
- Check file permissions and formats
- Try reloading data via API endpoint

**Voice alerts not working**  
- Check browser microphone permissions
- Verify audio is not muted
- Try different browser (Chrome recommended)

**Map not displaying**
- Check internet connection for map tiles
- Verify JavaScript is enabled
- Clear browser cache and reload

### Debug Mode
To enable debug logging, edit `app.py`:
```python
app.run(debug=True, host='0.0.0.0', port=5000)
```

## 🎯 Usage Scenarios

### Pre-flight Check
1. Start dashboard
2. Select your aircraft callsign
3. Verify position and system status
4. Check for nearby traffic
5. Set appropriate radar range

### En-route Monitoring
1. Monitor threat panel continuously
2. Listen for voice alerts
3. Track nearby aircraft positions
4. Adjust radar range as needed

### Emergency Situations
1. Press emergency button for mayday call
2. Monitor all nearby traffic
3. Use voice alerts for situational awareness
4. Follow standard emergency procedures

---

**SkyLink Pilot Dashboard** - Enhancing aviation safety through intelligent collision awareness! ✈️🚁📡