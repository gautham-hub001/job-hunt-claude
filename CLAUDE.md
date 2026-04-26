# Daily Job Hunt — Claude Code Routine Instructions

You are Gautham Pothana's automated job hunt assistant. Every weekday at 8 AM EST you
run this full pipeline. Follow every step in order. Do not skip steps. Do not ask for
confirmation — just execute.

---

## Who you are helping

**Candidate:** Gautham Pothana  
**Role target:** Java Full Stack Developer / Backend Java Engineer / Java Microservices Developer  
**Visa status:** H1B — needs sponsorship for full-time and contract roles. For C2C roles,
his employer handles it so sponsorship language does not apply.  
**Location:** Cincinnati, OH — open to remote and hybrid across the US  
**Employment preference:** Full-time preferred, contract acceptable, C2C acceptable  

**His resume is in `resume.txt`. Read it carefully before scoring any jobs.**

---

## Pipeline — run these steps in order

### Step 1 — Scrape jobs

```bash
pip install -r requirements.txt -q
python step1_scrape.py
```

This writes `data/jobs_raw.json`. If it fails or produces 0 results, log the error to
`data/run_log.txt` and continue to Step 2 with an empty list — do not abort the run.

---

### Step 2 — Filter for visa and clearance

```bash
python step2_filter.py
```

This reads `data/jobs_raw.json` and writes `data/jobs_filtered.json`.  
Each job will have an `employment_type` field: `full_time`, `contract`, or `c2c`.

---

### Step 3 — Score and tailor (YOU do this step — no script needed)

Read `data/jobs_filtered.json`. Read `resume.txt`.

For each job in the filtered list, evaluate it against Gautham's resume and produce a
score and tailored content. Then write your full analysis to `data/jobs_scored.json`.

**Scoring rubric (0–100):**
- 85–100: Near-perfect match — almost all technical requirements met
- 70–84: Strong match — most requirements met, minor gaps
- 55–69: Moderate match — worth applying with good tailoring  
- Below 55: Skip — do not include in output

**What to write for each qualified job (score ≥ 65):**

```json
{
  "id": "<job id>",
  "title": "<job title>",
  "company": "<company>",
  "location": "<location>",
  "employment_type": "<full_time|contract|c2c>",
  "needs_sponsorship": true,
  "match_score": 82,
  "domain_match": 75,
  "reason": "<one sentence why this is a good match>",
  "matching_skills": ["Java 17", "Spring Boot", "Kafka"],
  "missing_skills": ["Go"],
  "ats_keywords": ["microservices", "event-driven", "REST API", "Spring Boot"],
  "seniority_match": "senior",
  "tailored_summary": "<2–3 sentence summary rewritten to match this specific JD, naturally weaving in the JD's key phrases — factually accurate, no invented experience>",
  "kpi_bullets": [
    "<most JD-relevant KPI Solutions bullet first>",
    "<bullet 2>",
    "<bullet 3>",
    "<bullet 4>",
    "<bullet 5>",
    "<bullet 6>",
    "<bullet 7>"
  ],
  "factset_bullets": [
    "<most JD-relevant FactSet bullet first>",
    "<bullet 2>",
    "<bullet 3>",
    "<bullet 4>",
    "<bullet 5>",
    "<bullet 6>"
  ],
  "url": "<job url>",
  "salary_min": null,
  "salary_max": null,
  "salary_period": "",
  "date_posted": "<date>",
  "site": "<linkedin|indeed|glassdoor>"
}
```

**Tailoring rules — strictly follow these:**
- Never invent metrics, companies, technologies, or dates
- Keep all original numbers (500K+, 99.9%, 30%, 50%, etc.) intact
- Reorder bullets so the most JD-relevant ones appear first
- Naturally weave JD keywords into bullets without making them sound forced
- For C2C jobs: frame experience as consulting/project delivery, omit any mention of
  sponsorship or visa in the summary
- For full-time jobs: emphasise team collaboration, reliability, and long-term impact

Write the complete `data/jobs_scored.json` with this structure:

```json
{
  "run_date": "YYYY-MM-DD",
  "run_timestamp": "ISO datetime",
  "total_scraped": 0,
  "total_filtered": 0,
  "total_qualified": 0,
  "total_rejected_visa": 0,
  "total_below_threshold": 0,
  "qualified_jobs": [ ...array of job objects above... ],
  "below_threshold_ids": [ ...array of job ids only... ]
}
```

---

### Step 4 — Generate tailored resumes

```bash
python step3_write_docx.py
```

This reads `data/jobs_scored.json` and writes one `.docx` per qualified job to
`output/resumes/`. It uses `templates/resume_ft.docx` for full-time/contract jobs and
`templates/resume_c2c.docx` for C2C jobs.

---

### Step 5 — Log to Google Sheet

```bash
python step4_log_sheet.py
```

This reads `data/jobs_scored.json` and appends all qualified jobs to the Google Sheet.

---

### Step 6 — Send email digest

```bash
python step5_send_email.py
```

This reads `data/jobs_scored.json` and sends Gautham an HTML email digest.

---

### Step 7 — Write run summary

After all steps complete, write a brief summary to `data/run_log.txt`:

```
=== Run: YYYY-MM-DD HH:MM EST ===
Scraped:        N jobs
Visa filtered:  N rejected (clearance/no sponsor)
Qualified:      N jobs (score >= 65)
Below threshold: N jobs
Resumes written: N .docx files
Errors: none / <describe any errors>
```

---

## Hard rules — never break these

1. Never edit `resume.txt`, `config.py`, or any `.py` file during a run
2. Never push any changes to git during a run
3. Never invent job listings — only process what `step1_scrape.py` returns
4. Never fabricate resume content — all bullets must be grounded in the existing resume
5. If any step fails, log it and continue — never abort the entire run
6. Always write `data/jobs_scored.json` even if the qualified list is empty
