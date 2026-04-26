"""
step1_scrape.py
Scrapes job listings and writes data/jobs_raw.json.
Run by Claude Code as part of the daily routine.
"""

import json
import os
from datetime import datetime
from pathlib import Path

import pandas as pd
from jobspy import scrape_jobs

import config

OUT = Path("data/jobs_raw.json")
OUT.parent.mkdir(exist_ok=True)


def run():
    all_jobs: list[dict] = []
    seen:     set[str]   = set()
    errors:   list[str]  = []

    for keyword in config.SEARCH_KEYWORDS:
        print(f"  Scraping: '{keyword}' ...")
        try:
            df: pd.DataFrame = scrape_jobs(
                site_name                  = config.SCRAPE_SITES,
                search_term                = keyword,
                location                   = config.SEARCH_LOCATION,
                results_wanted             = config.RESULTS_PER_KEYWORD,
                hours_old                  = config.DAYS_OLD_MAX * 24,
                country_indeed             = "USA",
                linkedin_fetch_description = True,
                linkedin_email             = config.LINKEDIN_EMAIL or None,
                linkedin_password          = config.LINKEDIN_PASSWORD or None,
            )
        except Exception as e:
            msg = f"Scrape error for '{keyword}': {e}"
            print(f"    ⚠ {msg}")
            errors.append(msg)
            continue

        if df is None or df.empty:
            print(f"    No results.")
            continue

        for _, row in df.iterrows():
            job_id = _id(row)
            if job_id in seen:
                continue
            seen.add(job_id)
            all_jobs.append({
                "id":             job_id,
                "title":          _s(row, "title"),
                "company":        _s(row, "company"),
                "location":       _s(row, "location"),
                "job_type":       _s(row, "job_type"),
                "description":    _s(row, "description"),
                "url":            _s(row, "job_url"),
                "site":           _s(row, "site"),
                "date_posted":    _s(row, "date_posted"),
                "salary_min":     _s(row, "min_amount"),
                "salary_max":     _s(row, "max_amount"),
                "salary_period":  _s(row, "interval"),
                "search_keyword": keyword,
                "scraped_at":     datetime.now().isoformat(),
            })

        print(f"    {len(df)} found (unique total: {len(all_jobs)})")

    result = {
        "scraped_at":  datetime.now().isoformat(),
        "total":       len(all_jobs),
        "errors":      errors,
        "jobs":        all_jobs,
    }
    OUT.write_text(json.dumps(result, indent=2, default=str))
    print(f"\n✓ Wrote {len(all_jobs)} jobs to {OUT}")
    return len(all_jobs)


def _s(row, col: str) -> str:
    v = row.get(col, "")
    return "" if pd.isna(v) else str(v).strip()


def _id(row) -> str:
    url = _s(row, "job_url")
    return url or f"{_s(row,'company')}::{_s(row,'title')}::{_s(row,'location')}"


if __name__ == "__main__":
    n = run()
    print(f"Done — {n} jobs scraped.")
