@echo off
title PharmaTrack - Starting...
echo ================================================
echo   PharmaTrack Pharma Follow-up Manager
echo ================================================
echo.
echo Installing required packages...
pip install flask twilio schedule --quiet
echo.
echo Starting your app...
echo.
echo When you see "Running on http://localhost:5000"
echo open your browser and go to: http://localhost:5000
echo.
echo Keep this window open while using the app.
echo Press Ctrl+C to stop the app.
echo.
python app.py
pause
