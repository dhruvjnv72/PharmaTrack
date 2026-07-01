#!/bin/bash
echo "================================================"
echo "  PharmaTrack Pharma Follow-up Manager"
echo "================================================"
echo ""
echo "Installing required packages..."
pip3 install flask twilio schedule --quiet
echo ""
echo "Starting your app..."
echo ""
echo "Once running, open your browser and go to:"
echo "http://localhost:5000"
echo ""
echo "Keep this window open while using the app."
echo "Press Ctrl+C to stop the app."
echo ""
python3 app.py
