"""
step5_send_email.py
Reads data/jobs_scored.json and sends an HTML email digest via Gmail SMTP.
"""

import json
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime
from pathlib import Path

import config

IN = Path("data/jobs_scored.json")


def run():
    if not config.EMAIL_SENDER or not config.EMAIL_APP_PASSWORD:
        print("⚠ Email not configured — skipping")
        return

    if not IN.exists():
        print(f"⚠ {IN} not found — skipping email")
        return

    data     = json.loads(IN.read_text())
    jobs     = data.get("qualified_jobs", [])
    scraped  = data.get("total_scraped", 0)
    rejected = data.get("total_rejected_visa", 0)
    below    = data.get("total_below_threshold", 0)

    subject = (f"Job Hunt — {len(jobs)} matches today "
               f"({datetime.now().strftime('%b %d, %Y')})")
    html = _build_html(jobs, scraped, rejected, below)

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"]    = config.EMAIL_SENDER
    msg["To"]      = config.EMAIL_RECIPIENT
    msg.attach(MIMEText(html, "html"))

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(config.EMAIL_SENDER, config.EMAIL_APP_PASSWORD)
            smtp.sendmail(config.EMAIL_SENDER, config.EMAIL_RECIPIENT, msg.as_string())
        print(f"✓ Email sent to {config.EMAIL_RECIPIENT}")
    except Exception as e:
        print(f"⚠ Email failed: {e}")


def _build_html(jobs, scraped, rejected, below):
    date_str  = datetime.now().strftime("%A, %B %d, %Y")
    ft_count  = sum(1 for j in jobs if j.get("employment_type") == "full_time")
    c2c_count = sum(1 for j in jobs if j.get("employment_type") == "c2c")
    avg_score = int(sum(j.get("match_score", 0) for j in jobs) / len(jobs)) if jobs else 0

    cards = ""
    for job in sorted(jobs, key=lambda j: j.get("match_score", 0), reverse=True):
        score       = job.get("match_score", 0)
        score_color = "#16a34a" if score >= 80 else "#d97706" if score >= 65 else "#dc2626"
        et          = job.get("employment_type", "full_time")
        badge_color = {"full_time": "#2563eb", "contract": "#7c3aed", "c2c": "#059669"}.get(et, "#6b7280")
        badge_label = {"full_time": "Full-Time", "contract": "Contract", "c2c": "C2C"}.get(et, et)
        matching    = ", ".join(job.get("matching_skills", [])[:4])
        missing     = ", ".join(job.get("missing_skills", [])[:2])
        lo, hi      = job.get("salary_min"), job.get("salary_max")
        try:
            salary = f"${int(float(lo)):,}–${int(float(hi)):,}" if lo and hi else ""
        except Exception:
            salary = ""

        cards += f"""
        <div style="background:#fff;border:1px solid #e5e7eb;border-radius:10px;
                    padding:20px;margin-bottom:16px;">
          <div style="display:flex;justify-content:space-between;align-items:flex-start;
                      margin-bottom:10px;">
            <div>
              <span style="font-size:18px;font-weight:600;color:#111827;">
                {job.get('company','')}
              </span>
              <span style="background:{badge_color};color:#fff;font-size:11px;
                           padding:2px 8px;border-radius:20px;margin-left:8px;">
                {badge_label}
              </span>
              {'<span style="background:#059669;color:#fff;font-size:11px;padding:2px 8px;border-radius:20px;margin-left:4px;">No Sponsor Needed</span>' if not job.get('needs_sponsorship') else ''}
            </div>
            <div style="text-align:right;">
              <div style="font-size:24px;font-weight:700;color:{score_color};">{score}</div>
              <div style="font-size:11px;color:#6b7280;">match score</div>
            </div>
          </div>
          <div style="font-size:16px;color:#374151;margin-bottom:6px;">
            {job.get('title','')}
          </div>
          <div style="font-size:13px;color:#6b7280;margin-bottom:10px;">
            {job.get('location','')}
            {f' &nbsp;|&nbsp; {salary}' if salary else ''}
          </div>
          <div style="font-size:13px;margin-bottom:6px;">
            <strong>Matching:</strong> {matching}
          </div>
          {'<div style="font-size:13px;margin-bottom:8px;"><strong>Missing:</strong> <span style="color:#dc2626;">'+missing+'</span></div>' if missing else ''}
          <div style="font-size:12px;color:#6b7280;font-style:italic;margin-bottom:12px;">
            {job.get('reason','')}
          </div>
          <a href="{job.get('url','#')}"
             style="background:#2563eb;color:#fff;text-decoration:none;padding:8px 18px;
                    border-radius:6px;font-size:13px;font-weight:500;">
            View Job →
          </a>
        </div>"""

    no_jobs = ('<p style="color:#6b7280;text-align:center;padding:40px 0;">'
               'No qualifying jobs found today.</p>' if not jobs else "")

    def stat(label, val, color):
        return (f'<div style="background:#fff;border:1px solid #e5e7eb;border-radius:8px;'
                f'padding:14px;text-align:center;">'
                f'<div style="font-size:24px;font-weight:700;color:{color};">{val}</div>'
                f'<div style="font-size:12px;color:#6b7280;">{label}</div></div>')

    return f"""<!DOCTYPE html><html><body
      style="font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;
             background:#f9fafb;margin:0;padding:20px;">
      <div style="max-width:680px;margin:0 auto;">
        <div style="background:#1e40af;color:#fff;padding:28px 24px;
                    border-radius:12px;margin-bottom:20px;">
          <div style="font-size:22px;font-weight:700;">Daily Job Hunt Report</div>
          <div style="font-size:14px;opacity:.9;margin-top:4px;">{date_str}</div>
        </div>
        <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-bottom:20px;">
          {stat("Qualified", len(jobs), "#16a34a")}
          {stat("Full-Time", ft_count, "#2563eb")}
          {stat("C2C", c2c_count, "#059669")}
          {stat("Avg Score", avg_score, "#7c3aed")}
        </div>
        <div style="background:#fef9c3;border:1px solid #fde68a;border-radius:8px;
                    padding:12px 16px;margin-bottom:20px;font-size:13px;color:#92400e;">
          Pipeline: <strong>{scraped}</strong> scraped &nbsp;|&nbsp;
          <strong>{rejected}</strong> visa-filtered &nbsp;|&nbsp;
          <strong>{len(jobs)}</strong> qualified &nbsp;|&nbsp;
          <strong>{below}</strong> below threshold
        </div>
        <h2 style="font-size:18px;font-weight:600;color:#111827;margin:0 0 16px;">
          Today's Matches
        </h2>
        {cards}{no_jobs}
        <div style="text-align:center;font-size:12px;color:#9ca3af;margin-top:24px;
                    padding-top:16px;border-top:1px solid #e5e7eb;">
          Generated by Claude Code Routine · Update status in Google Sheets
        </div>
      </div></body></html>"""


if __name__ == "__main__":
    run()
