# Job Hunt Bot — Claude Code Routine Edition

Runs daily at **8 AM EST weekdays** using a **Claude Code Routine** on your existing
Pro subscription. No separate API billing. Claude Code itself scores jobs and tailors
your resume — the Python scripts handle only scraping, file generation, and output.

---

## What changed vs the API version

| | API version | This version |
|---|---|---|
| AI scoring & tailoring | Python calls Anthropic API | Claude Code does it directly |
| Scheduling | GitHub Actions cron | Claude Code Routine (Anthropic cloud) |
| Extra cost | ~$5/month API | $0 extra (uses your Pro subscription) |
| Setup | GitHub secrets + Actions | claude.ai/code/routines UI |

---

## File structure

```
job-hunt-bot/
├── CLAUDE.md               ← Instructions Claude Code reads on every run (the "brain")
├── resume.txt              ← Your full resume in plain text — Claude Code reads this
├── config.py               ← Search settings and credentials
├── requirements.txt        ← Python deps (no anthropic package needed)
├── .env.example            ← Template for environment variables
├── step1_scrape.py         ← Scrapes jobs → data/jobs_raw.json
├── step2_filter.py         ← Filters for H1B/clearance → data/jobs_filtered.json
├── step3_write_docx.py     ← Reads jobs_scored.json → output/resumes/*.docx
├── step4_log_sheet.py      ← Logs to Google Sheet
├── step5_send_email.py     ← Sends email digest
├── templates/
│   ├── resume_ft.docx      ← YOUR resume template (full-time/contract)
│   └── resume_c2c.docx     ← YOUR resume template (C2C variant)
├── data/                   ← Created at runtime (gitignored)
└── output/resumes/         ← Tailored .docx files (gitignored)
```

Claude Code reads `CLAUDE.md` and `resume.txt`, runs the step scripts, then **does the
job scoring and resume tailoring itself** (no API call — Claude IS the AI), then writes
`data/jobs_scored.json` which the remaining scripts read.

---

## Setup Guide

### Step 1 — Prerequisites

Make sure you have:
- **Claude Pro subscription** with Claude Code enabled
- **Python 3.11+** installed locally (for one-time template setup)
- **Git** installed

### Step 2 — Create your GitHub repo

```bash
git clone https://github.com/YOUR_USERNAME/job-hunt-bot.git
cd job-hunt-bot
# Copy all these files into it
git add .
git commit -m "Initial job hunt bot setup"
git push
```

### Step 3 — Get your credentials

**A) Google Sheets service account**
1. Go to https://console.cloud.google.com → Create project
2. Enable "Google Sheets API" and "Google Drive API"
3. IAM & Admin → Service Accounts → Create → Download JSON key
4. Go to https://sheets.google.com → Create a new blank sheet
5. Share the sheet with the service account email (`xxx@project.iam.gserviceaccount.com`)
6. Copy the Sheet ID from the URL (the long string between `/d/` and `/edit`)

**B) Gmail App Password**
1. Google Account → Security → 2-Step Verification (must be enabled)
2. Search "App passwords" → Create for "Mail"
3. Copy the 16-character password

### Step 4 — Prepare your resume templates

Copy your formatted `Gautham_Pothana_Resume_ATS.docx` to `templates/resume_ft.docx`.
Open it in Word and replace:
- Your summary paragraph text → `[[SUMMARY]]`
- Each KPI Solutions bullet → `[[KPI_BULLET_1]]` through `[[KPI_BULLET_7]]`
- Each FactSet bullet → `[[FACTSET_BULLET_1]]` through `[[FACTSET_BULLET_6]]`

Duplicate it as `templates/resume_c2c.docx` and adjust the framing for contract work.

Push the templates to GitHub (they're not gitignored — they're source files).

### Step 5 — Create the Claude Code Routine

1. Open **https://claude.ai/code** in your browser
2. Make sure Claude Code on the web is enabled (Settings → Claude Code)
3. Go to **https://claude.ai/code/routines**
4. Click **"New Routine"**
5. Set the **prompt** to:
   ```
   Follow the instructions in CLAUDE.md to run the daily job hunt pipeline.
   Read CLAUDE.md first, then execute every step in order.
   ```
6. Connect your **GitHub repository** (it will ask you to install the Claude GitHub App)
7. Add the **Google Drive connector** if you want Drive access (optional)
8. Under **Environment Variables**, add:
   - `GOOGLE_SERVICE_ACCOUNT_JSON` — paste the entire JSON from your key file (one line)
   - `GOOGLE_SHEET_ID` — your sheet ID
   - `EMAIL_SENDER` — your Gmail address
   - `EMAIL_APP_PASSWORD` — your 16-character app password
   - `EMAIL_RECIPIENT` — where to send the digest (can be the same address)
   - `LINKEDIN_EMAIL` — optional
   - `LINKEDIN_PASSWORD` — optional
9. Under **Schedule**, set:
   - Frequency: **Weekdays (Mon–Fri)**
   - Time: **8:00 AM** in your local timezone (Eastern)
10. Click **Save Routine**

### Step 6 — Test it manually

From the Routines page, click **"Run now"** to trigger a manual run.
You can watch it execute in real time at the session URL it generates.

Check:
- `data/jobs_raw.json` — was it created?
- `data/jobs_filtered.json` — did filtering run?
- `data/jobs_scored.json` — did Claude Code write its analysis?
- `output/resumes/` — are .docx files there?
- Your email inbox — did the digest arrive?
- Your Google Sheet — are rows added?

---

## Customising

All search settings are in `config.py`:

| Setting | Default | What it does |
|---------|---------|--------------|
| `SEARCH_KEYWORDS` | 5 role titles | Job titles to search |
| `JOB_MATCH_THRESHOLD` | 65 | Min score Claude uses to qualify a job |
| `DAYS_OLD_MAX` | 3 | Only jobs posted in last N days |
| `RESULTS_PER_KEYWORD` | 25 | Jobs fetched per keyword per site |

To change your resume content, edit `resume.txt` and push — Claude Code reads it fresh
on every run.

---

## Routine limits (Pro plan)

- **5 runs per day** — more than enough (you only need 1)
- Usage counts against your regular Pro subscription limit
- If you hit subscription limits mid-run, the routine pauses until your 5-hour reset

---

## Switching to the API version later

If Anthropic changes Pro/Claude Code access, switching is straightforward:
1. Add `anthropic>=0.40.0` back to `requirements.txt`
2. Restore `ai/role_matcher.py` and `ai/resume_tailor.py` from the API version
3. Add a `main.py` orchestrator
4. Add a GitHub Actions workflow for scheduling
5. Add `ANTHROPIC_API_KEY` to your secrets

All the scraping, filtering, and output code is identical between both versions.

---

## Troubleshooting

**Routine not firing:** Check claude.ai/code/routines — confirm it shows "Active" and
the next run time looks correct.

**jobs_scored.json missing:** Claude Code may have hit a usage limit mid-run. Check the
session URL for the error. Try running again when limits reset.

**Docx placeholders not replaced:** Open your template in Word and verify placeholders
are exactly `[[SUMMARY]]`, `[[KPI_BULLET_1]]`, etc. with no extra spaces.

**Google Sheets auth error:** Confirm both APIs are enabled in Google Cloud Console and
the sheet is shared with the service account email.

**LinkedIn blocking:** Remove `"linkedin"` from `SCRAPE_SITES` in `config.py`. Indeed
and Glassdoor alone give solid coverage.
