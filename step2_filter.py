"""
step2_filter.py
Reads data/jobs_raw.json, applies visa/clearance/C2C filters,
writes data/jobs_filtered.json.
"""

import json
import re
from pathlib import Path
from datetime import datetime

import config

IN  = Path("data/jobs_raw.json")
OUT = Path("data/jobs_filtered.json")


def run():
    raw = json.loads(IN.read_text()) if IN.exists() else {"jobs": []}
    jobs = raw.get("jobs", [])

    passed:   list[dict] = []
    rejected: list[dict] = []

    for job in jobs:
        text = _text(job)

        # Hard reject: clearance required
        hit = _find(text, config.CLEARANCE_PHRASES)
        if hit:
            job["filter_reason"] = f"clearance ({hit})"
            rejected.append(job)
            continue

        is_c2c      = bool(_find(text, config.C2C_PHRASES))
        is_contract = is_c2c or _contract_signals(text, job)

        if is_c2c:
            job["employment_type"]   = "c2c"
            job["needs_sponsorship"] = False
        elif is_contract:
            job["employment_type"]   = "contract"
            job["needs_sponsorship"] = True
        else:
            job["employment_type"]   = "full_time"
            job["needs_sponsorship"] = True

        # Hard reject: no-sponsorship language (unless C2C)
        no_sponsor = _find(text, config.NO_SPONSORSHIP_PHRASES)
        if no_sponsor and not is_c2c:
            job["filter_reason"] = f"no sponsorship ({no_sponsor})"
            rejected.append(job)
            continue

        passed.append(job)

    result = {
        "filtered_at":    datetime.now().isoformat(),
        "total_passed":   len(passed),
        "total_rejected": len(rejected),
        "jobs":           passed,
        "rejected":       rejected,
    }
    OUT.write_text(json.dumps(result, indent=2, default=str))
    print(f"✓ Filter: {len(passed)} passed, {len(rejected)} rejected → {OUT}")
    return len(passed), len(rejected)


def _text(job: dict) -> str:
    return " ".join([
        job.get("title", ""),
        job.get("description", ""),
        job.get("job_type", ""),
    ]).lower()


def _find(text: str, phrases: list) -> str | None:
    for p in phrases:
        if p.lower() in text:
            return p
    return None


def _contract_signals(text: str, job: dict) -> bool:
    jtype = job.get("job_type", "").lower()
    if "contract" in jtype or "temporary" in jtype:
        return True
    patterns = [r"\bcontract\b", r"\bcontractor\b", r"\bcontract.to.hire\b",
                r"\bc2h\b", r"\b\d+.month\b", r"\btemporary\b", r"\bstaffing\b"]
    return any(re.search(p, text) for p in patterns)


if __name__ == "__main__":
    p, r = run()
    print(f"Done — {p} passed, {r} rejected.")
