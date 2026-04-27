"""
step1_scrape.py
Scrapes job listings via Apify's LinkedIn Jobs Scraper actor.
No browser scraping, no blocking — works in any cloud sandbox.

Actor used: orgupdate/linkedin-jobs-scraper (free, no monthly rental)
Docs: https://apify.com/orgupdate/linkedin-jobs-scraper

Requires: APIFY_API_TOKEN in your Routine Instructions env block
"""

import json
import os
from datetime import datetime
from pathlib import Path

from apify_client import ApifyClient

import config

OUT = Path("data/jobs_raw.json")
OUT.parent.mkdir(exist_ok=True)

# Free actor — no rental fee required
ACTOR_ID = "orgupdate/linkedin-jobs-scraper"

DATE_POSTED_MAP = {
    1: "today",
    2: "2days",
    3: "3days",
    7: "week",
    30: "month",
}


def run():
    api_token = os.getenv("APIFY_API_TOKEN")
    if not api_token:
        print("⚠ APIFY_API_TOKEN not set — skipping scrape")
        _write_empty()
        return 0

    client    = ApifyClient(api_token)
    all_jobs: list[dict] = []
    seen:     set[str]   = set()
    errors:   list[str]  = []

    date_posted = DATE_POSTED_MAP.get(config.DAYS_OLD_MAX, "3days")

    for keyword in config.SEARCH_KEYWORDS:
        print(f"  Scraping via Apify: '{keyword}' ...")
        try:
            run_input = {
                "countryName":   "usa",
                "locationName":  "United States",
                "includeKeyword": keyword,
                "datePosted":    date_posted,
                "pagesToFetch":  max(1, config.RESULTS_PER_KEYWORD // 25),
            }

            run        = client.actor(ACTOR_ID).call(run_input=run_input)
            dataset_id = run.get("defaultDatasetId")

            if not dataset_id:
                msg = f"No dataset returned for '{keyword}'"
                print(f"    ⚠ {msg}")
                errors.append(msg)
                continue

            items = list(client.dataset(dataset_id).iterate_items())
            print(f"    Raw results: {len(items)}")

            for item in items:
                job_id = item.get("URL") or item.get("url") or _make_id(item)
                if not job_id or job_id in seen:
                    continue
                seen.add(job_id)

                all_jobs.append({
                    "id":             job_id,
                    "title":          _get(item, ["job_title", "title", "jobTitle"]),
                    "company":        _get(item, ["company_name", "company", "companyName"]),
                    "location":       _get(item, ["location"]),
                    "job_type":       _get(item, ["job_type", "jobType", "employmentType"]),
                    "description":    _get(item, ["description", "jobDescription", "job_description"]),
                    "url":            _get(item, ["URL", "url", "jobUrl"]),
                    "site":           "linkedin",
                    "date_posted":    _get(item, ["date", "postedAt", "date_posted"]),
                    "salary_min":     _parse_salary_min(item),
                    "salary_max":     _parse_salary_max(item),
                    "salary_period":  _get(item, ["salaryPeriod", "salary_period"]),
                    "search_keyword": keyword,
                    "scraped_at":     datetime.now().isoformat(),
                })

            print(f"    Added (unique total: {len(all_jobs)})")

        except Exception as e:
            msg = f"Apify error for '{keyword}': {e}"
            print(f"    ⚠ {msg}")
            errors.append(msg)
            continue

    result = {
        "scraped_at": datetime.now().isoformat(),
        "total":      len(all_jobs),
        "errors":     errors,
        "jobs":       all_jobs,
    }
    OUT.write_text(json.dumps(result, indent=2, default=str))
    print(f"\n✓ Wrote {len(all_jobs)} jobs to {OUT}")
    return len(all_jobs)


def _get(item: dict, keys: list, default: str = "") -> str:
    for k in keys:
        v = item.get(k)
        if v and str(v).strip():
            return str(v).strip()
    return default


def _make_id(item: dict) -> str:
    return (f"{_get(item, ['company_name','company'])}"
            f"::{_get(item, ['job_title','title'])}"
            f"::{_get(item, ['location'])}")


def _parse_salary_min(item: dict) -> str:
    raw = _get(item, ["salary", "salaryMin", "salary_min", "compensation"])
    if not raw:
        return ""
    parts = raw.replace("$", "").replace(",", "").split("-")
    try:
        return str(int(float(parts[0].strip().split()[0])))
    except Exception:
        return ""


def _parse_salary_max(item: dict) -> str:
    raw = _get(item, ["salary", "salaryMax", "salary_max", "compensation"])
    if not raw:
        return ""
    parts = raw.replace("$", "").replace(",", "").split("-")
    if len(parts) < 2:
        return ""
    try:
        return str(int(float(parts[1].strip().split()[0])))
    except Exception:
        return ""


def _write_empty():
    OUT.write_text(json.dumps({
        "scraped_at": datetime.now().isoformat(),
        "total": 0,
        "errors": ["APIFY_API_TOKEN not set"],
        "jobs": [],
    }, indent=2))


if __name__ == "__main__":
    n = run()
    print(f"Done — {n} jobs scraped.")