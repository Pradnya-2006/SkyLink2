"""
Drone Dashboard Module
Creates HTML dashboard visualization for real-time drone alerts and collision warnings.
"""

import json
import os
import webbrowser
from datetime import datetime
from typing import List, Dict
from .alert_translator import DroneAlertTranslator

class DroneDashboard:
    def __init__(self):
        self.alert_translator = DroneAlertTranslator()
        
    def generate_dashboard(self, drone_data: List[Dict], plane_data: List[Dict], output_dir: str = "outputs"):
        """Generate complete drone dashboard with alerts"""
        
        # Process alerts using the translator
        all_alerts = self.alert_translator.process_multiple_alerts(drone_data, plane_data)
        
        # Create dashboard HTML
        dashboard_html = self._create_dashboard_html(all_alerts, drone_data)
        
        # Save dashboard
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"drone_dashboard_{timestamp}.html"
        filepath = os.path.join(output_dir, filename)
        
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(dashboard_html)
            
        # Save alerts as JSON
        alerts_filepath = self.alert_translator.export_alerts_json(all_alerts, output_dir)
            
        print(f"✅ Drone Dashboard saved: {filepath}")
        print(f"📄 Alerts JSON saved: {alerts_filepath}")
        
        # Auto-open dashboard
        webbrowser.open(f'file://{os.path.abspath(filepath)}')
        
        return filepath, all_alerts
    
    def _create_dashboard_html(self, alerts_data: List[Dict], drone_data: List[Dict]) -> str:
        """Create HTML dashboard with live alerts"""
        
        html_template = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>SkyLink Drone Command Center</title>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Roboto+Mono:wght@300;400;500&display=swap" rel="stylesheet">
            <style>
                * {{
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                }}
                
                body {{ 
                    font-family: 'Roboto Mono', monospace; 
                    background: linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 50%, #16213e 100%);
                    color: #00cc66;
                    overflow-x: hidden;
                    min-height: 100vh;
                }}
                
                .header {{ 
                    text-align: center; 
                    padding: 20px 0;
                    background: linear-gradient(90deg, rgba(0,204,102,0.1) 0%, rgba(64,128,255,0.1) 50%, rgba(138,43,226,0.1) 100%);
                    border-bottom: 2px solid #4080ff;
                    margin-bottom: 30px;
                    position: relative;
                }}
                
                .header::before {{
                    content: '';
                    position: absolute;
                    top: 0;
                    left: 0;
                    right: 0;
                    height: 2px;
                    background: linear-gradient(90deg, transparent 0%, #4080ff 50%, transparent 100%);
                    animation: scan 3s linear infinite;
                }}
                
                @keyframes scan {{
                    0% {{ transform: translateX(-100%); }}
                    100% {{ transform: translateX(100%); }}
                }}
                
                .header h1 {{
                    font-family: 'Orbitron', monospace;
                    font-size: 2.5em;
                    font-weight: 900;
                    color: #4080ff;
                    text-shadow: 0 0 20px #4080ff, 0 0 40px #4080ff;
                    margin-bottom: 10px;
                    letter-spacing: 3px;
                }}
                
                .header p {{
                    font-size: 1.2em;
                    color: #7dd3fc;
                    text-transform: uppercase;
                    letter-spacing: 2px;
                }}
                
                .main-container {{
                    padding: 0 20px;
                }}
                
                .timestamp {{
                    position: fixed;
                    top: 20px;
                    right: 20px;
                    background: rgba(0,0,0,0.8);
                    border: 1px solid #4080ff;
                    padding: 15px;
                    border-radius: 8px;
                    font-family: 'Orbitron', monospace;
                    font-size: 14px;
                    z-index: 1000;
                    box-shadow: 0 0 20px rgba(64,128,255,0.3);
                }}
                
                .stats-grid {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                    gap: 20px;
                    margin: 30px 0;
                }}
                
                .stat-card {{
                    background: linear-gradient(145deg, #1a1a2e 0%, #16213e 100%);
                    border: 1px solid #4080ff;
                    border-radius: 12px;
                    padding: 20px;
                    text-align: center;
                    position: relative;
                    overflow: hidden;
                    transition: all 0.3s ease;
                }}
                
                .stat-card::before {{
                    content: '';
                    position: absolute;
                    top: 0;
                    left: -100%;
                    width: 100%;
                    height: 100%;
                    background: linear-gradient(90deg, transparent, rgba(64,128,255,0.1), transparent);
                    transition: left 0.5s ease;
                }}
                
                .stat-card:hover {{
                    transform: translateY(-5px);
                    box-shadow: 0 10px 30px rgba(64,128,255,0.2);
                }}
                
                .stat-card:hover::before {{
                    left: 100%;
                }}
                
                .stat-card h3 {{
                    font-family: 'Orbitron', monospace;
                    color: #7dd3fc;
                    font-size: 0.9em;
                    margin-bottom: 10px;
                    text-transform: uppercase;
                    letter-spacing: 1px;
                }}
                
                .stat-card .number {{
                    font-family: 'Orbitron', monospace;
                    font-size: 2.5em;
                    font-weight: 700;
                    color: #00cc66;
                    text-shadow: 0 0 10px #00cc66;
                }}
                
                .drones-grid {{ 
                    display: grid; 
                    grid-template-columns: repeat(auto-fit, minmax(450px, 1fr)); 
                    gap: 25px;
                    margin-top: 30px;
                }}
                
                .drone-operator-screen {{ 
                    background: linear-gradient(145deg, #0d1117 0%, #1a1a2e 100%);
                    border: 2px solid #4080ff;
                    border-radius: 15px;
                    padding: 0;
                    position: relative;
                    overflow: hidden;
                    box-shadow: 0 0 30px rgba(64,128,255,0.2);
                    transition: all 0.3s ease;
                }}
                
                .drone-operator-screen:hover {{
                    transform: scale(1.02);
                    box-shadow: 0 0 40px rgba(64,128,255,0.3);
                }}
                
                .drone-header {{
                    background: linear-gradient(90deg, #4080ff 0%, #8a2be2 100%);
                    color: #fff;
                    padding: 15px 20px;
                    font-family: 'Orbitron', monospace;
                    font-weight: 700;
                    font-size: 1.1em;
                    text-transform: uppercase;
                    letter-spacing: 2px;
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                }}
                
                .drone-status-led {{
                    width: 12px;
                    height: 12px;
                    border-radius: 50%;
                    animation: pulse-led 2s infinite;
                }}
                
                @keyframes pulse-led {{
                    0%, 100% {{ opacity: 1; transform: scale(1); }}
                    50% {{ opacity: 0.5; transform: scale(1.2); }}
                }}
                
                .drone-body {{
                    padding: 20px;
                }}
                
                .drone-vital-stats {{
                    display: grid;
                    grid-template-columns: 1fr 1fr;
                    gap: 15px;
                    margin-bottom: 20px;
                }}
                
                .vital-stat {{
                    background: rgba(64,128,255,0.05);
                    border: 1px solid rgba(64,128,255,0.3);
                    border-radius: 8px;
                    padding: 12px;
                    text-align: center;
                }}
                
                .vital-stat .label {{
                    font-size: 0.8em;
                    color: #7dd3fc;
                    text-transform: uppercase;
                    letter-spacing: 1px;
                }}
                
                .vital-stat .value {{
                    font-family: 'Orbitron', monospace;
                    font-size: 1.3em;
                    font-weight: 700;
                    color: #00cc66;
                    margin-top: 5px;
                }}
                
                .alerts-section {{
                    background: rgba(0,0,0,0.3);
                    border: 1px solid rgba(64,128,255,0.2);
                    border-radius: 10px;
                    padding: 15px;
                }}
                
                .alerts-header {{
                    font-family: 'Orbitron', monospace;
                    color: #ff6b6b;
                    font-size: 1em;
                    margin-bottom: 15px;
                    text-transform: uppercase;
                    letter-spacing: 1px;
                    text-align: center;
                }}
                
                .alert-item {{ 
                    margin: 10px 0; 
                    padding: 15px; 
                    border-radius: 8px; 
                    border-left: 4px solid;
                    background: rgba(0,0,0,0.4);
                    position: relative;
                    overflow: hidden;
                }}
                
                .critical {{ 
                    border-left-color: #ff0000; 
                    background: linear-gradient(90deg, rgba(255,0,0,0.1) 0%, rgba(255,0,0,0.05) 100%);
                    animation: critical-pulse 1s infinite;
                }}
                
                .high {{ 
                    border-left-color: #ff6600; 
                    background: linear-gradient(90deg, rgba(255,102,0,0.1) 0%, rgba(255,102,0,0.05) 100%);
                }}
                
                .medium {{ 
                    border-left-color: #ffff00; 
                    background: linear-gradient(90deg, rgba(255,255,0,0.1) 0%, rgba(255,255,0,0.05) 100%);
                }}
                
                .low {{ 
                    border-left-color: #00ff00; 
                    background: linear-gradient(90deg, rgba(0,255,0,0.1) 0%, rgba(0,255,0,0.05) 100%);
                }}
                
                .safe {{ 
                    border-left-color: #00cc66; 
                    background: linear-gradient(90deg, rgba(0,204,102,0.1) 0%, rgba(0,204,102,0.05) 100%);
                }}
                
                @keyframes critical-pulse {{
                    0%, 100% {{ box-shadow: 0 0 5px rgba(255,0,0,0.5); }}
                    50% {{ box-shadow: 0 0 20px rgba(255,0,0,0.8), inset 0 0 20px rgba(255,0,0,0.1); }}
                }}
                
                .status-indicator {{
                    display: inline-block;
                    width: 10px;
                    height: 10px;
                    border-radius: 50%;
                    margin-right: 8px;
                    animation: pulse-indicator 2s infinite;
                }}
                
                @keyframes pulse-indicator {{
                    0%, 100% {{ opacity: 1; }}
                    50% {{ opacity: 0.6; }}
                }}
                
                .alert-header {{
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    margin-bottom: 8px;
                }}
                
                .alert-distance {{
                    font-family: 'Orbitron', monospace;
                    font-weight: 700;
                    font-size: 1.1em;
                }}
                
                .alert-guidance {{
                    font-size: 0.9em;
                    line-height: 1.4;
                    margin: 8px 0;
                    color: #e0e0e0;
                }}
                
                .alert-details {{
                    font-size: 0.75em;
                    color: #888;
                    margin-top: 8px;
                    padding-top: 8px;
                    border-top: 1px solid rgba(255,255,255,0.1);
                }}
                
                .all-clear {{
                    text-align: center;
                    padding: 30px;
                    color: #00cc66;
                    font-family: 'Orbitron', monospace;
                    font-size: 1.2em;
                    text-transform: uppercase;
                    letter-spacing: 2px;
                }}
                
                .radar-grid {{
                    position: absolute;
                    top: 50%;
                    left: 50%;
                    transform: translate(-50%, -50%);
                    width: 100px;
                    height: 100px;
                    opacity: 0.1;
                    pointer-events: none;
                }}
                
                .radar-grid::before,
                .radar-grid::after {{
                    content: '';
                    position: absolute;
                    top: 50%;
                    left: 50%;
                    transform: translate(-50%, -50%);
                    border: 1px solid #4080ff;
                }}
                
                .radar-grid::before {{
                    width: 80px;
                    height: 80px;
                    border-radius: 50%;
                }}
                
                .radar-grid::after {{
                    width: 2px;
                    height: 80px;
                }}
                
                @media (max-width: 768px) {{
                    .drones-grid {{
                        grid-template-columns: 1fr;
                    }}
                    
                    .stats-grid {{
                        grid-template-columns: repeat(2, 1fr);
                    }}
                    
                    .header h1 {{
                        font-size: 1.8em;
                    }}
                }}
            </style>
        </head>
        <body>
            <div class="timestamp">
                <div>LAST UPDATED: {datetime.now().strftime("%H:%M:%S")}</div>
                <div>DATE: {datetime.now().strftime("%Y-%m-%d")}</div>
            </div>
            
            <div class="header">
                <h1>🛰️ SKYLINK COMMAND CENTER</h1>
                <p>Real-Time Drone Operations & Collision Avoidance System</p>
            </div>
            
            <div class="main-container">
                <div class="stats-grid">
                    <div class="stat-card">
                        <h3>Active Drones</h3>
                        <div class="number">{len(drone_data)}</div>
                    </div>
                    <div class="stat-card">
                        <h3>Total Alerts</h3>
                        <div class="number">{sum(drone['alert_count'] for drone in alerts_data)}</div>
                    </div>
                    <div class="stat-card">
                        <h3>Critical Alerts</h3>
                        <div class="number">{sum(1 for drone in alerts_data for alert in drone['alerts'] if alert['danger_level'] == 'CRITICAL')}</div>
                    </div>
                    <div class="stat-card">
                        <h3>High Priority</h3>
                        <div class="number">{sum(1 for drone in alerts_data for alert in drone['alerts'] if alert['danger_level'] == 'HIGH')}</div>
                    </div>
                </div>
                
                <div class="drones-grid">
                    {self._generate_drone_operator_screens(alerts_data)}
                </div>
            </div>
            
            <script>
                // Auto refresh every 30 seconds
                setTimeout(function(){{ location.reload(); }}, 30000);
                
                // Add scanning effect
                setInterval(function() {{
                    const stats = document.querySelectorAll('.stat-card');
                    stats.forEach((stat, index) => {{
                        setTimeout(() => {{
                            stat.style.transform = 'scale(1.05)';
                            setTimeout(() => {{
                                stat.style.transform = 'scale(1)';
                            }}, 200);
                        }}, index * 100);
                    }});
                }}, 5000);
            </script>
        </body>
        </html>
        """
        
        return html_template
    
    def _generate_drone_operator_screens(self, alerts_data: List[Dict]) -> str:
        """Generate drone operator screens that look like real drone control interfaces"""
        screens_html = ""
        
        for drone in alerts_data:
            drone_id = drone['drone_id']
            location = drone['location']
            altitude = drone['altitude']
            alerts = drone['alerts']
            highest_priority = drone['highest_priority']
            
            # Determine status LED color, screen border, and header colors based on alert level
            alert_level_styles = {
                'CRITICAL': {
                    'border_color': '#ff0000',
                    'header_bg': 'linear-gradient(90deg, #ff0000 0%, #cc0000 100%)',
                    'led_color': '#ff0000'
                },
                'HIGH': {
                    'border_color': '#ff6600', 
                    'header_bg': 'linear-gradient(90deg, #ff6600 0%, #cc5200 100%)',
                    'led_color': '#ff6600'
                },
                'MEDIUM': {
                    'border_color': '#ffff00',
                    'header_bg': 'linear-gradient(90deg, #ffff00 0%, #cccc00 100%)',
                    'led_color': '#ffff00'
                },
                'LOW': {
                    'border_color': '#00cc66',
                    'header_bg': 'linear-gradient(90deg, #00cc66 0%, #009944 100%)',
                    'led_color': '#00cc66'
                },
                'SAFE': {
                    'border_color': '#4080ff',
                    'header_bg': 'linear-gradient(90deg, #4080ff 0%, #8a2be2 100%)',
                    'led_color': '#00cc66'
                }
            }
            
            styles = alert_level_styles.get(highest_priority, alert_level_styles['SAFE'])
            border_color = styles['border_color']
            header_bg = styles['header_bg']
            led_color = styles['led_color']
            
            # Calculate additional stats
            battery_level = 85  # Mock battery level
            signal_strength = 95  # Mock signal strength
            flight_time = "00:15:32"  # Mock flight time
            
            alerts_html = ""
            if alerts:
                for alert in alerts:
                    danger_class = alert['danger_level'].lower()
                    alerts_html += f"""
                    <div class="alert-item {danger_class}">
                        <div class="alert-header">
                            <div>
                                <span class="status-indicator" style="background-color: {alert['color_code']};"></span>
                                <strong>{alert['danger_level']}</strong> - {alert['plane_info']['callsign']}
                            </div>
                            <div class="alert-distance">{alert['distance_km']} km</div>
                        </div>
                        <div class="alert-guidance">
                            {alert['guidance']}
                        </div>
                        <div class="alert-details">
                            <div>✈️ Aircraft Alt: {alert['plane_info']['altitude']}m | Speed: {alert['plane_info']['speed']} m/s | Heading: {alert['plane_info']['heading']}°</div>
                            <div>🚁 Drone Alt: {alert['drone_info']['altitude']}m | Alert ID: {alert['alert_id'][-8:]}</div>
                        </div>
                    </div>
                    """
            else:
                alerts_html = '''
                <div class="all-clear">
                    <div>🟢 ALL SYSTEMS CLEAR</div>
                    <div style="font-size: 0.8em; margin-top: 10px;">No Aircraft Threats Detected</div>
                </div>
                '''
            
            screens_html += f"""
            <div class="drone-operator-screen" style="border-color: {border_color};">
                <div class="radar-grid"></div>
                
                <div class="drone-header" style="background: {header_bg};">
                    <div>🚁 DRONE {drone_id}</div>
                    <div style="display: flex; align-items: center; gap: 10px;">
                        <span>STATUS: {highest_priority}</span>
                        <div class="drone-status-led" style="background-color: {led_color};"></div>
                    </div>
                </div>
                
                <div class="drone-body">
                    <div class="drone-vital-stats">
                        <div class="vital-stat">
                            <div class="label">LATITUDE</div>
                            <div class="value">{location[0]:.6f}°</div>
                        </div>
                        <div class="vital-stat">
                            <div class="label">LONGITUDE</div>
                            <div class="value">{location[1]:.6f}°</div>
                        </div>
                        <div class="vital-stat">
                            <div class="label">ALTITUDE</div>
                            <div class="value">{altitude}m</div>
                        </div>
                        <div class="vital-stat">
                            <div class="label">BATTERY</div>
                            <div class="value">{battery_level}%</div>
                        </div>
                        <div class="vital-stat">
                            <div class="label">SIGNAL</div>
                            <div class="value">{signal_strength}%</div>
                        </div>
                        <div class="vital-stat">
                            <div class="label">FLIGHT TIME</div>
                            <div class="value">{flight_time}</div>
                        </div>
                    </div>
                    
                    <div class="alerts-section">
                        <div class="alerts-header">
                            🚨 COLLISION ALERTS ({len(alerts)})
                        </div>
                        {alerts_html}
                    </div>
                </div>
            </div>
            """
        
        return screens_html