"""
step4_log_sheet.py
Reads data/jobs_scored.json and appends qualified jobs to Google Sheets.
"""

import json
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
from pathlib import Path

import config

IN = Path("data/jobs_scored.json")

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

HEADERS = [
    "Date", "Company", "Title", "Type", "Score", "Domain Match",
    "Location", "Salary", "H1B Needed", "URL", "Resume File",
    "Status", "Matching Skills", "Missing Skills", "ATS Keywords", "Notes",
]


def run():
    if not IN.exists():
        print(f"⚠ {IN} not found")
        return 0

    if not config.GOOGLE_SHEET_ID:
        print("⚠ GOOGLE_SHEET_ID not set — skipping")
        return 0

    data = json.loads(IN.read_text())
    jobs = data.get("qualified_jobs", [])
    if not jobs:
        print("No qualified jobs to log.")
        return 0

    try:
        creds  = Credentials.from_service_account_info(
            json.loads(config.GOOGLE_SERVICE_ACCOUNT), scopes=SCOPES)
        client = gspread.authorize(creds)
        sheet  = client.open_by_key(config.GOOGLE_SHEET_ID).sheet1

        if not sheet.row_values(1) or sheet.row_values(1)[0] != "Date":
            sheet.insert_row(HEADERS, 1)
    except Exception as e:
        print(f"⚠ Google Sheets auth error: {e}")
        return 0

    added = 0
    for job in jobs:
        try:
            row = _to_row(job)
            sheet.append_row(row, value_input_option="USER_ENTERED")
            added += 1
        except Exception as e:
            print(f"  ⚠ Failed to log {job.get('company')}: {e}")

    print(f"✓ Logged {added} jobs to Google Sheet")
    return added


def _to_row(job: dict) -> list:
    lo, hi = job.get("salary_min"), job.get("salary_max")
    per = job.get("salary_period", "")
    try:
        salary = (f"${int(float(lo)):,}–${int(float(hi)):,} {per}"
                  if lo and hi else f"${int(float(lo)):,}+ {per}" if lo else "")
    except (ValueError, TypeError):
        salary = ""

    return [
        datetime.now().strftime("%Y-%m-%d"),
        job.get("company", ""),
        job.get("title", ""),
        job.get("employment_type", "").replace("_", " ").title(),
        job.get("match_score", ""),
        job.get("domain_match", ""),
        job.get("location", ""),
        salary,
        "Yes" if job.get("needs_sponsorship") else "No (C2C)",
        job.get("url", ""),
        job.get("resume_file", ""),
        "To Apply",
        ", ".join(job.get("matching_skills", [])[:5]),
        ", ".join(job.get("missing_skills", [])[:3]),
        ", ".join(job.get("ats_keywords", [])[:6]),
        job.get("reason", ""),
    ]


if __name__ == "__main__":
    n = run()
    print(f"Done — {n} rows added.")
