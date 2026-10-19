# PharmaTrack

A patient follow-up manager for hospitals and clinics. It replaces day-to-day Excel visit sheets, where one patient's history ends up scattered across many rows, with a small web app that keeps everything about a patient in one place.

All the code is in the [`pharma_app`](pharma_app) folder.

## What it does

- One record per patient, with their full visit history
- A dashboard that shows today's follow-ups at the top and flags overdue ones in red
- Add, edit, search and filter patients
- Mark a case as resolved; resolved cases move to an archive
- Export a report as a text file
- Optional WhatsApp morning alerts through Twilio
- `import_excel.py` imports existing Excel data so a clinic can switch over without retyping

## Built with

Python, Flask, a single HTML template, JSON file storage, Twilio (optional alerts).

## Run it

You need Python installed.

```bash
cd pharma_app
pip install flask twilio schedule
python app.py
```

Then open <http://localhost:5000>. On Windows you can also double-click `START_APP.bat`.

To import an existing sheet, use `IMPORT_DATA.bat` or run `python import_excel.py`.

## WhatsApp alerts (optional)

Alerts need your own Twilio account. Put your credentials in your own environment or settings; never commit real keys to the repository. `whatsapp_alert.py` contains placeholders only.

## Notes

- Patient data is stored in `pharma_app/data/` as JSON. Do not publish real patient records in a public repository.
- This is a small tool, not a certified medical-records system.
