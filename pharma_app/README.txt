================================================
  PharmaTrack - Pharma Follow-up Manager
  Setup Guide
================================================

WHAT THIS APP DOES:
- Tracks all your patient visits and follow-ups
- Shows today's follow-ups automatically at the top
- Flags overdue patients in red
- One-click to mark a case as resolved
- Archives resolved patients for company records
- Search and filter patients instantly
- WhatsApp morning alerts (optional setup)
- Export reports as text file


STEP 1 — INSTALL PYTHON (One-time only)
---------------------------------------
1. Go to: https://www.python.org/downloads/
2. Click "Download Python" (latest version)
3. Run the installer
   IMPORTANT: Check the box that says "Add Python to PATH"
4. Click Install


STEP 2 — START THE APP
-----------------------
Windows:
  Double-click "START_APP.bat"
  Wait for it to say "Running on http://localhost:5000"
  Open Chrome/Firefox and go to: http://localhost:5000

Mac:
  Open Terminal, drag the "start_app.sh" file into it, press Enter
  Open Chrome/Safari and go to: http://localhost:5000


STEP 3 — USE THE APP
---------------------
- Dashboard: See today's and overdue follow-ups at a glance
- Add Patient: Enter new patient visit details
- Follow-ups: See all active follow-ups, search, filter
- Resolved: Browse all closed cases (company archive)
- Settings: Set up WhatsApp alerts


STEP 4 — WHATSAPP ALERTS (Optional)
-------------------------------------
1. Sign up FREE at: https://www.twilio.com
2. Go to Messaging > Try WhatsApp Sandbox
3. Follow the setup (send a WhatsApp to their number)
4. Open "whatsapp_alert.py" in Notepad
5. Fill in your ACCOUNT_SID, AUTH_TOKEN, and your phone number
6. Double-click or run: python whatsapp_alert.py
7. Keep that window open — it sends alerts every morning at 8 AM!


CHANGING REP NAMES
------------------
Open "app.py" in Notepad
Find this line near the top:
  REPS = ["Select Rep", "Manager", "Rep 1", "Rep 2"]
Change "Rep 1" and "Rep 2" to your actual rep names
Save the file and restart the app


YOUR DATA
---------
All patient data is stored in: data/patients.json
This is a simple text file — back it up regularly!
Copy it to Google Drive or a USB stick weekly.


SUPPORT
-------
Built with Python + Flask
Data stored locally on your computer (private & secure)
No internet required to run (except for WhatsApp alerts)

================================================
