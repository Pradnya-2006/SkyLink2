@echo off
echo.
echo ================================================================
echo                   SKYLINK PILOT DASHBOARD
echo ================================================================
echo.
echo Starting the pilot dashboard server...
echo Dashboard will be available at: http://localhost:5000
echo.
echo Press Ctrl+C to stop the server
echo ================================================================
echo.

cd /d "%~dp0"
python launch_dashboard.py

pause