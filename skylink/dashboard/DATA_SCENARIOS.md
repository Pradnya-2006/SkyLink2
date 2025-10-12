# SkyLink Pilot Dashboard - Data Scenarios

## 🎯 Two Distinct Operating Modes

The pilot dashboard operates in two distinct modes to demonstrate both realistic collision detection and controlled testing scenarios.

---

## 🧪 TEST MODE (Default)

### Overview
- **Location**: New York City (JFK Airport vicinity)
- **Coordinates**: 40.7128°N, 74.0060°W
- **Purpose**: Demonstrate collision detection logic with guaranteed alerts
- **Data Type**: Synthetic, carefully crafted collision scenarios

### Aircraft Configuration
```
UAL100  - Primary aircraft (pilot view) - 200m altitude
DAL201  - Delta flight                  - 250m altitude  
AAL302  - American flight               - 300m altitude
JBU403  - JetBlue flight               - 350m altitude
SWA504  - Southwest flight             - 400m altitude
UAL605  - United flight                - 280m altitude
AAL706  - American flight              - 320m altitude
```

### Drone Threat Levels
```
DRONE_CRITICAL  - 0.05km from UAL100   - CRITICAL threat (immediate danger)
DRONE_HIGH_1    - 0.15km from DAL201   - HIGH threat    (close approach)
DRONE_HIGH_2    - 0.18km from AAL302   - HIGH threat    (close approach)
DRONE_MED_1     - 0.35km from JBU403   - MEDIUM threat  (moderate risk)
DRONE_MED_2     - 0.38km from SWA504   - MEDIUM threat  (moderate risk)
DRONE_LOW_1     - 0.65km from UAL605   - LOW threat     (distant but monitored)
DRONE_LOW_2     - 0.72km from AAL706   - LOW threat     (distant but monitored)
DRONE_SAFE_1    - 1.20km from aircraft - SAFE           (no threat)
DRONE_SAFE_2    - 1.35km from aircraft - SAFE           (no threat)
```

### Expected Voice Alerts
1. **"Traffic alert! Critical threat from drone DRONE_CRITICAL at distance 0.1 kilometers"** (spoken twice)
2. **"Traffic advisory. Drone DRONE_HIGH_1 at distance 0.2 kilometers"** (spoken twice)
3. Additional alerts for medium-level threats

### Test Features
- ✅ Guaranteed collision alerts for demonstration
- ✅ Multiple risk levels (Critical, High, Medium, Low)
- ✅ Realistic aircraft callsigns and flight patterns
- ✅ Voice alert testing with cooldown system
- ✅ Geographic clustering for visual impact

---

## 📡 REAL DATA MODE

### Overview
- **Location**: Bangalore, India region (filtered)
- **Coordinates**: 12.8°N to 13.1°N, 77.4°E to 77.7°E  
- **Purpose**: Real-world collision monitoring with actual flight data
- **Data Type**: Live aircraft positions and drone operations

### Data Sources
```
Aircraft: ../plane_data/opensky_live_states.csv
- OpenSky Network live flight tracking data
- Commercial aviation traffic
- Real callsigns, positions, altitudes, velocities
- Filtered to Bangalore region for relevance

Drones: ../drone_data/dummy_drone_dataset_30.csv
- Simulated drone operations in Bangalore airspace
- Realistic flight patterns and altitudes
- Multiple time steps showing drone movement
```

### Real Data Characteristics
- **Aircraft Count**: Up to 20 filtered aircraft
- **Drone Count**: 15 active drones
- **Altitude Range**: 100m - 1000m (filtered for proximity to drones)
- **Coverage Area**: Bangalore metropolitan area
- **Update Frequency**: Static snapshot (real-time in production)

### Expected Behavior
- ⚠️ May have few or no collision alerts (depends on actual traffic)
- ✅ Realistic aircraft callsigns (AI, 6E, SG, UK prefixes)
- ✅ Actual flight paths and altitudes
- ✅ Geographic accuracy for Bangalore region
- ✅ Variable threat levels based on actual positions

---

## 🎮 Switching Between Modes

### Via Dashboard Controls
1. **Test Mode Button**: Click to toggle between modes
   - Orange = Test Mode (synthetic collision scenario)
   - Green = Real Data Mode (filtered live data)

2. **Visual Indicators**:
   - Map overlay shows current mode
   - Button color changes with mode
   - Voice announcements confirm mode switch

### Voice Confirmations
- **Test Mode**: *"Test scenario loaded. 7 aircraft, 9 drones in New York City area"*
- **Real Mode**: *"Real flight data loaded. X aircraft, Y drones from live sources"*

---

## 📊 Collision Detection Logic (Both Modes)

### Threat Level Thresholds
```javascript
Critical:  < 0.1km horizontal, < 30m vertical
High:      < 0.3km horizontal, < 50m vertical  
Medium:    < 0.5km horizontal, < 100m vertical
Low:       < 1.0km horizontal, < 150m vertical
```

### Voice Alert System
- **Maximum Repeats**: 2 times per unique threat
- **Cooldown Period**: 30 seconds between same alert
- **Alert Priority**: Critical > High > Medium > Low
- **Manual Control**: "Clear Voice" button to reset/stop

---

## 🛠️ Technical Implementation

### Data Loading Process
```python
1. Initialize dashboard service
2. Load test scenario data (synthetic)
3. Load real CSV data (filtered)
4. Set default mode (test)
5. Create switching mechanism
```

### API Endpoints
```
GET  /api/pilot-data          - Current aircraft and threats
POST /api/toggle-data-source  - Switch between test/real
GET  /api/data-info          - Information about data sources
GET  /api/collision-demo     - Detailed collision analysis
```

---

## 🎯 Use Cases

### Test Mode - Ideal For:
- **Training**: Learning collision detection systems
- **Demonstration**: Showing alert capabilities
- **Development**: Testing voice alert logic
- **Education**: Understanding threat assessment
- **Validation**: Verifying system responses

### Real Data Mode - Ideal For:
- **Operations**: Actual flight monitoring
- **Analysis**: Real traffic pattern study  
- **Validation**: Real-world system testing
- **Research**: Airspace utilization analysis
- **Production**: Live collision monitoring

---

## 🔍 Troubleshooting Data Modes

### Test Mode Issues
```
Problem: No alerts in test mode
Solution: Test mode guarantees alerts - check voice settings

Problem: Wrong aircraft position
Solution: Test mode uses NYC coordinates (40.71, -74.00)
```

### Real Data Mode Issues  
```
Problem: No aircraft visible
Solution: Check if CSV files exist and contain Bangalore region data

Problem: No collision alerts
Solution: Normal - real data may not have active threats
```

### General Issues
```
Problem: Mode switch not working
Solution: Check browser console for API errors

Problem: Voice alerts not stopping
Solution: Use "Clear Voice" button or toggle voice off/on
```

---

**Both modes demonstrate the SkyLink collision detection system's capability to provide real-time airspace safety monitoring with appropriate voice alerts and visual indicators!** ✈️🚁📡