import os
import json
from datetime import datetime

DB_FILE = "career_data.json"

def get_default_db():
    return {
        "applications": [],
        "resume_history": [],
        "chat_sessions": [],
        "interview_sessions": []
    }

def load_db():
    if not os.path.exists(DB_FILE):
        db = get_default_db()
        save_db(db)
        return db
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            # Ensure all required keys exist
            defaults = get_default_db()
            for key in defaults:
                if key not in data:
                    data[key] = defaults[key]
            return data
    except Exception:
        return get_default_db()

def save_db(db):
    try:
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(db, f, indent=4, ensure_ascii=False)
        return True
    except Exception:
        return False

# -----------------------------
# Operations helpers
# -----------------------------

def add_application(title, company, date_applied, status, score):
    db = load_db()
    app_id = str(len(db["applications"]) + 1)
    db["applications"].append({
        "id": app_id,
        "title": title,
        "company": company,
        "date": date_applied,
        "status": status,  # Applied, Interviewing, Offer, Rejected, Pending
        "score": score
    })
    save_db(db)
    return db["applications"]

def update_application_status(app_id, new_status):
    db = load_db()
    for app in db["applications"]:
        if app["id"] == app_id:
            app["status"] = new_status
            break
    save_db(db)
    return db["applications"]

def delete_application(app_id):
    db = load_db()
    db["applications"] = [app for app in db["applications"] if app["id"] != app_id]
    # Re-index ids
    for i, app in enumerate(db["applications"]):
        app["id"] = str(i + 1)
    save_db(db)
    return db["applications"]

def add_resume_history(version_name, score, keyword_coverage, missing_count):
    db = load_db()
    db["resume_history"].append({
        "version": version_name,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "score": score,
        "coverage": keyword_coverage,
        "missing_count": missing_count
    })
    save_db(db)
    return db["resume_history"]
