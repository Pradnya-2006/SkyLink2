# 🚁✈️ SkyLink Setup Guide

## Quick Start for Friends & Collaborators

### Prerequisites
- **Python 3.8+** (recommended: Python 3.12)
- **Git** installed on your system

### 🚀 Installation Steps

#### 1. Clone the Repository
```bash
git clone https://github.com/Pradnya-2006/SkyLink2.git
cd SkyLink2/skylink
```

#### 2. Create Virtual Environment (Recommended)
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

#### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

#### 4. Run the Application
```bash
python unified_app.py
```

### 🌐 Access the Dashboards

Once running, open your browser and visit:
- **🏠 Main Hub:** http://localhost:5000
- **✈️ Pilot Dashboard:** http://localhost:5000/pilot-dashboard  
- **🚁 Drone Dashboard:** http://localhost:5000/drone-dashboard

### 🎯 What You'll See

#### Main Hub (`/`)
- System status overview
- Quick access to both dashboards
- Data source toggle (Test vs Real data)

#### Pilot Dashboard (`/pilot-dashboard`)
- Cockpit-style interface with radar display
- Live aircraft and drone tracking
- Collision alerts and voice announcements
- Interactive controls for range and voice settings

#### Drone Dashboard (`/drone-dashboard`)
- Drone operator interface
- Multi-drone monitoring
- Flight path visualization
- Alert management system

### 🔧 Troubleshooting

#### Common Issues:

**Port Already in Use:**
```bash
# Change port in unified_app.py (line ~1040)
app.run(debug=True, host='0.0.0.0', port=5001)  # Use different port
```

**Module Import Errors:**
```bash
# Make sure you're in the skylink directory
cd SkyLink2/skylink
python unified_app.py
```

**Permission Errors:**
- Run terminal as Administrator (Windows)
- Use `sudo` for installation commands (macOS/Linux)

#### Dependencies Not Installing:
```bash
# Upgrade pip first
pip install --upgrade pip
pip install -r requirements.txt
```

### 📁 Project Structure
```
SkyLink2/
└── skylink/
    ├── unified_app.py          # Main Flask application
    ├── requirements.txt        # Python dependencies
    ├── templates/              # HTML templates
    │   ├── index.html         # Main hub page
    │   ├── pilot_dashboard.html
    │   └── drone_dashboard.html
    ├── collision_module/       # Core collision detection
    ├── drone_data/            # Sample drone datasets
    ├── plane_data/            # Sample aircraft data
    └── outputs/               # Generated reports & maps
```

### 🎮 Demo Data vs Real Data

**Test Mode (Default):**
- Uses sample datasets from `drone_data/` and `plane_data/`
- Concentrated around NYC area for demo purposes
- ~6 aircraft, ~9 drones

**Real Mode:**
- Fetches live flight data (when available)
- Global coverage with proximity filtering
- Dynamic data updates

### 🚨 System Requirements
- **RAM:** 2GB minimum, 4GB recommended
- **Storage:** 500MB for code + dependencies
- **Network:** Internet connection for real data mode
- **Browser:** Modern browser (Chrome, Firefox, Edge, Safari)

### 🤝 Contributing
1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### 📞 Support
If you encounter issues:
1. Check this SETUP.md guide
2. Review the console output for error messages
3. Ensure all dependencies are installed correctly
4. Try running in a fresh virtual environment

---
**Happy Flying!** 🛩️✨