"""
config.py — Search settings and credentials.
No Anthropic API key needed — Claude Code IS the AI.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# ─── Google Sheets ────────────────────────────────────────────────────────────
GOOGLE_SERVICE_ACCOUNT = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")
GOOGLE_SHEET_ID        = os.getenv("GOOGLE_SHEET_ID")

# ─── Email digest ─────────────────────────────────────────────────────────────
EMAIL_SENDER      = os.getenv("EMAIL_SENDER")
EMAIL_APP_PASSWORD = os.getenv("EMAIL_APP_PASSWORD")
EMAIL_RECIPIENT   = os.getenv("EMAIL_RECIPIENT")

# ─── Job search ───────────────────────────────────────────────────────────────
SEARCH_KEYWORDS = [
    "Java Full Stack Developer",
    "Java Spring Boot Developer",
    "Senior Java Developer",
    "Backend Java Engineer",
    "Java Microservices Developer",
]

SEARCH_LOCATION     = "United States"
RESULTS_PER_KEYWORD = 25
DAYS_OLD_MAX        = 3
SCRAPE_SITES        = ["linkedin", "indeed", "glassdoor"]
JOB_MATCH_THRESHOLD = 65   # Claude Code skips jobs it scores below this

# ─── Visa / clearance phrases ─────────────────────────────────────────────────
NO_SPONSORSHIP_PHRASES = [
    "no sponsorship", "no visa sponsorship", "must be authorized to work",
    "must be a us citizen", "us citizen only", "us citizenship required",
    "only us citizens", "permanent resident only", "green card required",
    "gc required", "not able to sponsor", "unable to sponsor",
    "no opting", "no opt",
]

CLEARANCE_PHRASES = [
    "security clearance", "secret clearance", "top secret", "ts/sci",
    "dod clearance", "active clearance", "clearance required", "public trust",
    "must hold clearance",
]

C2C_PHRASES = [
    "c2c", "corp to corp", "corp-to-corp", "1099", "w2 or c2c", "w2/c2c",
    "independent contractor", "contract-to-hire", "c2h",
]

# LinkedIn credentials (optional — improves result quality)
LINKEDIN_EMAIL    = os.getenv("LINKEDIN_EMAIL", "")
LINKEDIN_PASSWORD = os.getenv("LINKEDIN_PASSWORD", "")
