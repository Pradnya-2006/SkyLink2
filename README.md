# 🚁✈️ SkyLink - Drone & Aircraft Collision Detection System

A unified web application for monitoring aircraft and drone traffic with real-time collision detection and alert systems.

## ⚡ Quick Start

### For Windows Users:
```bash
# 1. Clone the repository
git clone https://github.com/Pradnya-2006/SkyLink2.git
cd SkyLink2/skylink

# 2. Run the setup script
setup.bat

# 3. Start the application
venv\Scripts\activate
python unified_app.py
```

### For macOS/Linux Users:
```bash
# 1. Clone the repository
git clone https://github.com/Pradnya-2006/SkyLink2.git
cd SkyLink2/skylink

# 2. Run the setup script
chmod +x setup.sh
./setup.sh

# 3. Start the application
source venv/bin/activate
python unified_app.py
```

## 🌐 Access Points

Once running, visit these URLs in your browser:

- **🏠 Main Hub:** http://localhost:5000
- **✈️ Pilot Dashboard:** http://localhost:5000/pilot-dashboard
- **🚁 Drone Dashboard:** http://localhost:5000/drone-dashboard

## 🎯 Features

### 🏠 Main Hub
- System status overview
- Aircraft and drone count monitoring
- Quick navigation to specialized dashboards

### ✈️ Pilot Dashboard
- **Cockpit-style interface** with radar display
- **Live tracking** of nearby aircraft and drones
- **Voice alerts** for collision warnings
- **Interactive controls** for range and system settings
- **Real-time data** updates every few seconds

### 🚁 Drone Dashboard
- **Multi-drone monitoring** interface
- **Flight path visualization** on interactive maps
- **Alert management** system
- **Real-time status** of drone fleet operations

## 🔧 System Requirements

- **Python 3.8+** (recommended: Python 3.12)
- **2GB RAM** minimum (4GB recommended)
- **Modern web browser** (Chrome, Firefox, Edge, Safari)
- **Internet connection** (for real data mode)

## 📦 Dependencies

All dependencies are listed in `requirements.txt`:
- Flask (web framework)
- Pandas (data processing)
- NumPy (numerical computations)
- Folium (map visualization)
- Geopy (geographic calculations)

## 🚨 Safety Features

- **Real-time collision detection** between aircraft and drones
- **Proximity alerts** with configurable thresholds
- **Voice announcements** for critical situations
- **Visual indicators** for threat levels
- **Automatic data updates** for situational awareness

## 📖 Detailed Setup

For detailed setup instructions, troubleshooting, and advanced configuration, see [SETUP.md](SETUP.md).

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

If you encounter any issues:
1. Check the [SETUP.md](SETUP.md) guide
2. Review console output for error messages
3. Ensure all dependencies are correctly installed
4. Try running in a fresh virtual environment

---

**Built with ❤️ for aviation safety** ✈️🚁