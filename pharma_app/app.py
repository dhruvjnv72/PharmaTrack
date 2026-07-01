from flask import Flask, render_template, request, jsonify, redirect, url_for, Response
import json, os, uuid
from datetime import datetime, date

app = Flask(__name__)
DATA_FILE = os.path.join(os.path.dirname(__file__), 'data', 'patients.json')
PROFILE_FILE = os.path.join(os.path.dirname(__file__), 'data', 'profile.json')
REPS = ["Select Rep", "Manager", "Rep 1", "Rep 2"]

def load_data():
    if not os.path.exists(DATA_FILE):
        return {"active": [], "resolved": []}
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_data(data):
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def load_profile():
    if not os.path.exists(PROFILE_FILE):
        return {"clinic_name": "PharmaTrack", "user_name": "", "contact": "", "address": "", "tagline": ""}
    with open(PROFILE_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_profile(profile):
    os.makedirs(os.path.dirname(PROFILE_FILE), exist_ok=True)
    with open(PROFILE_FILE, 'w', encoding='utf-8') as f:
        json.dump(profile, f, indent=2)

def extract_followup_date(text):
    import re
    from datetime import date
    if not text:
        return None
    text=str(text).strip()
    invalid={"already","not interested","not intrerested","incoming not available","all good","not answered","call not answered","rude response","invalid","will come soon"}
    if text.lower() in invalid:
        return None
    m=re.search(r'(\d{1,2})[./-](\d{1,2})[./-](\d{2,4})',text)
    if not m:
        return None
    d,mth,y=map(int,m.groups())
    if y<100:
        y+=2000
    try:
        return date(y,mth,d)
    except:
        return None

def get_status(followup_date_str):
    followup=extract_followup_date(followup_date_str)
    if followup is None:
        return "upcoming"
    today=date.today()
    if followup<today:
        return "overdue"
    elif followup==today:
        return "today"
    else:
        return "upcoming"

@app.route('/')
def index():
    data = load_data()
    profile = load_profile()
    active = data.get("active", [])
    for p in active:
        p['status'] = get_status(p.get('followup_date', ''))
    active_sorted = sorted(active, key=lambda x: extract_followup_date(x.get("followup_date")) or date.max)
    today_count   = sum(1 for p in active if p['status'] == 'today')
    overdue_count = sum(1 for p in active if p['status'] == 'overdue')
    upcoming_count= sum(1 for p in active if p['status'] == 'upcoming')
    resolved = data.get("resolved", [])

    # Build 3-day upcoming dashboard
    from datetime import timedelta
    upcoming_days = []
    day_configs = [
        (0, "Today", "#d97706", "#fef3c7"),
        (1, "Tomorrow", "#2563eb", "#dbeafe"),
        (2, "Day After Tomorrow", "#7c3aed", "#ede9fe"),
    ]
    for offset, label, color, bg in day_configs:
        day = date.today() + timedelta(days=offset)
        day_patients = [p for p in active if extract_followup_date(p.get("followup_date")) == day]
        upcoming_days.append({
            "label": label,
            "date_display": day.strftime("%d %b"),
            "date_str": day_str,
            "color": color,
            "bg": bg,
            "patients": day_patients,
            "count": len(day_patients)
        })

    return render_template('index.html',
        patients=active_sorted, resolved=resolved,
        today_count=today_count, overdue_count=overdue_count,
        upcoming_count=upcoming_count, total_active=len(active),
        total_resolved=len(resolved), reps=REPS,
        today=date.today().strftime("%Y-%m-%d"),
        profile=profile,
        upcoming_days=upcoming_days)

@app.route('/add_patient', methods=['POST'])
def add_patient():
    data = load_data()
    followup_count = int(request.form.get('followup_count', 1))

    # Collect all follow-up dates
    followup_dates = []
    first_date = request.form.get('followup_date', '').strip()
    if first_date:
        followup_dates.append(first_date)
    for i in range(2, followup_count + 1):
        d = request.form.get(f'followup_date_{i}', '').strip()
        if d:
            followup_dates.append(d)

    # Base patient data
    base = {
        "name": request.form.get('name','').strip(),
        "uhid": request.form.get('uhid','').strip(),
        "old_new": request.form.get('old_new','New').strip(),
        "age": request.form.get('age','').strip(),
        "sex": request.form.get('sex','').strip(),
        "phone": request.form.get('phone','').strip(),
        "doctor": request.form.get('doctor','').strip(),
        "area": request.form.get('area','').strip(),
        "product": request.form.get('product','').strip(),
        "diagnosis": request.form.get('diagnosis','').strip(),
        "medicine": request.form.get('medicine','').strip(),
        "current_status": request.form.get('current_status','').strip(),
        "rep": request.form.get('rep','').strip(),
        "notes": request.form.get('notes','').strip(),
        "visit_date": request.form.get('visit_date',''),
        "followup_count": followup_count,
        "visit_history": [request.form.get('visit_date', date.today().strftime("%Y-%m-%d"))],
        "added_on": date.today().strftime("%Y-%m-%d")
    }

    if not followup_dates:
        # No dates given — save once with empty followup
        patient = dict(base)
        patient['id'] = str(uuid.uuid4())
        patient['followup_date'] = ''
        data["active"].append(patient)
    else:
        # Create one entry per follow-up date
        for i, fdate in enumerate(followup_dates):
            patient = dict(base)
            patient['id'] = str(uuid.uuid4())
            patient['followup_date'] = fdate
            patient['followup_label'] = f"Follow-up {i+1} of {len(followup_dates)}" if len(followup_dates) > 1 else ""
            data["active"].append(patient)

    save_data(data)
    return redirect(url_for('index') + '#followups')

@app.route('/resolve/<patient_id>', methods=['POST'])
def resolve(patient_id):
    data = load_data()
    patient = next((p for p in data["active"] if p['id'] == patient_id), None)
    if patient:
        patient['resolved_on'] = date.today().strftime("%Y-%m-%d")
        data["resolved"].append(patient)
        data["active"] = [p for p in data["active"] if p['id'] != patient_id]
        save_data(data)
    return jsonify({"success": True})

@app.route('/unresolve/<patient_id>', methods=['POST'])
def unresolve(patient_id):
    data = load_data()
    patient = next((p for p in data["resolved"] if p['id'] == patient_id), None)
    if patient:
        patient.pop('resolved_on', None)
        data["active"].append(patient)
        data["resolved"] = [p for p in data["resolved"] if p['id'] != patient_id]
        save_data(data)
    return jsonify({"success": True})

@app.route('/delete/<patient_id>', methods=['POST'])
def delete(patient_id):
    data = load_data()
    data["active"] = [p for p in data.get("active",[]) if p['id'] != patient_id]
    save_data(data)
    return jsonify({"success": True})

@app.route('/patient/<patient_id>')
def get_patient(patient_id):
    data = load_data()
    all_patients = data.get("active",[]) + data.get("resolved",[])
    patient = next((p for p in all_patients if p['id'] == patient_id), None)
    if patient: return jsonify(patient)
    return jsonify({"error": "Not found"}), 404

@app.route('/save_profile', methods=['POST'])
def save_profile_route():
    profile = {
        "clinic_name": request.form.get('clinic_name','PharmaTrack').strip(),
        "user_name": request.form.get('user_name','').strip(),
        "contact": request.form.get('contact','').strip(),
        "address": request.form.get('address','').strip(),
        "tagline": request.form.get('tagline','').strip(),
    }
    save_profile(profile)
    return redirect(url_for('index') + '#settings')

@app.route('/api/today_followups')
def today_followups():
    data = load_data()
    today = date.today()
    today_p=[p for p in data.get("active",[]) if extract_followup_date(p.get("followup_date"))==today]
    overdue=[p for p in data.get("active",[]) if extract_followup_date(p.get("followup_date")) is not None and extract_followup_date(p.get("followup_date"))<today]
    return jsonify({"today": today_p, "overdue": overdue})

@app.route('/export')
def export():
    data = load_data()
    lines = ["ACTIVE FOLLOW-UPS\n" + "="*60]
    for p in sorted(data.get("active",[]), key=lambda x: x.get('followup_date','')):
        lines.append(f"Name: {p['name']} | UHID: {p.get('uhid','')} | Age: {p.get('age','')} | Sex: {p.get('sex','')}")
        lines.append(f"Phone: {p.get('phone','')} | Area: {p.get('area','')} | Rep: {p.get('rep','')}")
        lines.append(f"Visit: {p.get('visit_date','')} | Follow-up: {p.get('followup_date','')} | Count: {p.get('followup_count',1)}")
        lines.append(f"Diagnosis: {p.get('diagnosis','')} | Status: {p.get('current_status','')}")
        lines.append(f"Notes: {p.get('notes','')}\n")
    lines.append("\nRESOLVED CASES\n" + "="*60)
    for p in data.get("resolved",[]):
        lines.append(f"Name: {p['name']} | Resolved: {p.get('resolved_on','')}")
    content = "\n".join(lines)
    return Response(content, mimetype='text/plain',
        headers={"Content-Disposition": "attachment;filename=pharma_report.txt"})

if __name__ == '__main__':
    os.makedirs('data', exist_ok=True)
    print("\n" + "="*50)
    print("  PharmaTrack is RUNNING!")
    print("  Open: http://localhost:5000")
    print("="*50 + "\n")
    app.run(debug=False, host='0.0.0.0', port=5000)

@app.route('/edit_patient/<patient_id>', methods=['POST'])
def edit_patient(patient_id):
    data = load_data()
    followup_count = int(request.form.get('followup_count', 1))

    # Collect all follow-up dates
    followup_dates = []
    first_date = request.form.get('followup_date', '').strip()
    if first_date:
        followup_dates.append(first_date)
    for i in range(2, followup_count + 1):
        d = request.form.get(f'followup_date_{i}', '').strip()
        if d:
            followup_dates.append(d)

    all_lists = [data.get("active", []), data.get("resolved", [])]
    for lst in all_lists:
        patient = next((p for p in lst if p['id'] == patient_id), None)
        if patient:
            # Update base fields
            patient.update({
                "name": request.form.get('name', patient['name']).strip(),
                "uhid": request.form.get('uhid', '').strip(),
                "old_new": request.form.get('old_new', '').strip(),
                "age": request.form.get('age', '').strip(),
                "sex": request.form.get('sex', '').strip(),
                "phone": request.form.get('phone', '').strip(),
                "doctor": request.form.get('doctor', '').strip(),
                "area": request.form.get('area', '').strip(),
                "product": request.form.get('product', '').strip(),
                "diagnosis": request.form.get('diagnosis', '').strip(),
                "medicine": request.form.get('medicine', '').strip(),
                "current_status": request.form.get('current_status', '').strip(),
                "rep": request.form.get('rep', '').strip(),
                "notes": request.form.get('notes', '').strip(),
                "visit_date": request.form.get('visit_date', ''),
                "followup_date": followup_dates[0] if followup_dates else '',
                "followup_count": followup_count,
            })
            # Append new visit date to history
            new_vdate = request.form.get('visit_date', '')
            hist = patient.get('visit_history', [])
            if new_vdate and new_vdate not in hist:
                hist.append(new_vdate); hist.sort()
            patient['visit_history'] = hist

            # If multiple follow-up dates, create extra sibling entries
            if len(followup_dates) > 1:
                base = dict(patient)
                for i, fdate in enumerate(followup_dates[1:], start=2):
                    sibling = dict(base)
                    sibling['id'] = str(uuid.uuid4())
                    sibling['followup_date'] = fdate
                    sibling['followup_label'] = f"Follow-up {i} of {len(followup_dates)}"
                    data["active"].append(sibling)
                patient['followup_label'] = f"Follow-up 1 of {len(followup_dates)}"
            else:
                patient['followup_label'] = ''

            save_data(data)
            # Check if request wants JSON (fetch) or redirect (form POST)
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({"success": True})
            return redirect(url_for('index') + '#followups')
    return jsonify({"error": "Not found"}), 404
