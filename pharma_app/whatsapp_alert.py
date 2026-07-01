"""
================================================
  PharmaTrack — WhatsApp Morning Alert
================================================

SETUP INSTRUCTIONS (One-time, 10 minutes):

1. Go to https://www.twilio.com and create a FREE account
2. In Twilio Console:
   - Get your ACCOUNT_SID and AUTH_TOKEN from dashboard
   - Go to Messaging > Try it out > Send a WhatsApp message
   - Follow the sandbox setup (send a WhatsApp to their number)
3. Fill in your credentials below
4. Run this script: python whatsapp_alert.py
5. It will send you a WhatsApp every morning at 8 AM automatically!

INSTALL REQUIREMENTS:
   pip install twilio schedule

================================================
"""

import json
import os
import schedule
import time
from datetime import datetime, date

# ============================================
#   FILL IN YOUR DETAILS HERE
# ============================================
TWILIO_ACCOUNT_SID = "YOUR_ACCOUNT_SID_HERE"
TWILIO_AUTH_TOKEN  = "YOUR_AUTH_TOKEN_HERE"
TWILIO_FROM        = "whatsapp:+14155238886"   # Twilio sandbox number (keep as is)
YOUR_WHATSAPP      = "whatsapp:+91XXXXXXXXXX"  # Your WhatsApp number with country code
ALERT_TIME         = "08:00"                   # Time to send alert (24hr format)
# ============================================

DATA_FILE = os.path.join(os.path.dirname(__file__), 'data', 'patients.json')

def load_data():
    if not os.path.exists(DATA_FILE):
        return {"active": [], "resolved": []}
    with open(DATA_FILE, 'r') as f:
        return json.load(f)

def build_message():
    data = load_data()
    active = data.get("active", [])
    today_str = date.today().strftime("%Y-%m-%d")
    today_display = date.today().strftime("%d %B %Y")

    today_patients = [p for p in active if p.get('followup_date') == today_str]
    overdue_patients = [p for p in active if p.get('followup_date', '') < today_str]

    lines = [f"💊 *PharmaTrack Daily Report*"]
    lines.append(f"📅 {today_display}\n")

    if today_patients:
        lines.append(f"🟡 *TODAY'S FOLLOW-UPS ({len(today_patients)})*")
        for p in today_patients:
            lines.append(f"• {p['name']} — Dr. {p['doctor']} ({p['area']})")
            lines.append(f"  Rep: {p['rep']} | Product: {p['product']}")
        lines.append("")

    if overdue_patients:
        lines.append(f"🔴 *OVERDUE — URGENT ({len(overdue_patients)})*")
        for p in overdue_patients:
            lines.append(f"• {p['name']} — due {p['followup_date']}")
            lines.append(f"  Dr. {p['doctor']} | Rep: {p['rep']}")
        lines.append("")

    if not today_patients and not overdue_patients:
        lines.append("✅ No follow-ups due today. You're all clear!")

    lines.append(f"📊 Total active: {len(active)} patients")
    lines.append("Open PharmaTrack → http://localhost:5000")

    return "\n".join(lines)

def send_whatsapp_alert():
    try:
        from twilio.rest import Client
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        message_body = build_message()
        message = client.messages.create(
            body=message_body,
            from_=TWILIO_FROM,
            to=YOUR_WHATSAPP
        )
        print(f"[{datetime.now().strftime('%H:%M')}] WhatsApp alert sent! SID: {message.sid}")
        print("\n--- MESSAGE PREVIEW ---")
        print(message_body)
        print("----------------------\n")
    except ImportError:
        print("ERROR: Twilio not installed. Run: pip install twilio")
    except Exception as e:
        print(f"ERROR sending WhatsApp: {e}")
        print("Check your credentials in whatsapp_alert.py")

def preview_message():
    """Preview today's message without sending"""
    print("\n--- TODAY'S MESSAGE PREVIEW ---")
    print(build_message())
    print("--------------------------------\n")

if __name__ == "__main__":
    print("="*50)
    print("  PharmaTrack WhatsApp Alert Service")
    print(f"  Will send alert every day at {ALERT_TIME}")
    print("="*50)

    # Show preview immediately on startup
    preview_message()

    # Send one immediately (optional — comment out if you don't want)
    print("Sending test WhatsApp now...")
    send_whatsapp_alert()

    # Schedule daily alerts
    schedule.every().day.at(ALERT_TIME).do(send_whatsapp_alert)
    print(f"\nScheduler running. Next alert at {ALERT_TIME} daily.")
    print("Keep this window open. Press Ctrl+C to stop.\n")

    while True:
        schedule.run_pending()
        time.sleep(30)
