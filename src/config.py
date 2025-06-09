import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# GitHub API Configuration
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_OWNER = os.getenv("GITHUB_OWNER")
GITHUB_REPO = os.getenv("GITHUB_REPO")

GITHUB_API_URL = "https://api.github.com"
GITHUB_REPO_URL = f"{GITHUB_API_URL}/repos/{GITHUB_OWNER}/{GITHUB_REPO}"
GITHUB_API_PULLS_URL = f"{GITHUB_REPO_URL}/pulls"

HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}


# Files Configuration
ROOT_LOG_DIR = Path("../logs")
ROOT_DATA_DIR = Path("../data")
EXTRACTED_FILE_NAME = "pr_data.json"
PROCESSED_FILE_NAME = "pr_report_csv"

CSV_HEADERS = ["PR_number", "PR_title", "Author", "Merge date", "CR_Passed", "CHECKS_PASSED"]



