import json
import logging
from pathlib import Path

import requests

import config
from schemas.constants import PrInfo

logger = logging.getLogger(__name__)


def github_get(url: str, params: dict = None) -> dict:
    """Wrapper around requests.get that includes headers and basic error‐handling."""
    response = requests.get(url, headers=config.HEADERS, params=params, timeout=20)
    response.raise_for_status()
    return response.json()


def get_all_github_pages(url: str, params: dict = None, per_page: int = 100, page: int = 1):
    """
    Handle GitHub pagination. Yields items from all pages.
    params: url, dict of query parameters. Injecting 'page' and 'per_page'.
    """
    if not params:
        params = {}

    query = params.copy()
    query["per_page"] = per_page

    while True:
        query["page"] = page
        response_data = github_get(url=url, params=query)

        if not response_data:
            break

        if not isinstance(response_data, list):
            yield response_data
            break

        yield from response_data

        if len(response_data) < per_page:
            break

        page += 1


def fetch_merged_prs() -> list[dict]:
    """
    Fetches all merged pull requests from the repo, filters by closed state, and verifying actual merge status using
    merged_at date.
    return: merged_pr list
    """

    merged_pr = []
    for pr in get_all_github_pages(config.GITHUB_API_PULLS_URL, params={"state": "closed"}):
        if pr.get("merged_at"):
            merged_pr.append(pr)
    return merged_pr


def fetch_reviews(pr_number: int) -> list[dict]:
    """
    Fetches all reviews by PR number.
    returns a list of dicts, each is a PR review.
    """
    url = f"{config.GITHUB_API_PULLS_URL}/{pr_number}/reviews"
    return list(get_all_github_pages(url))


def fetch_check_suites(sha: str) -> list[dict]:
    """
    Fetches the latest check_suites by the HEAD_SHA of the PR.
    """
    url = f"{config.GITHUB_REPO_URL}/commits/{sha}/check-suites"
    check_suites = next(get_all_github_pages(url=url), {}).get("check_suites", [])
    return check_suites


def run_extract(output_path: Path, input_path: Path = None):

    all_data = []
    merged_prs = fetch_merged_prs()
    pr_len = len(merged_prs)

    for idx, pr in enumerate(merged_prs, 1):
        logger.info(f"Extracting PR {idx}/{pr_len}, PR #{pr['number']}")
        info = PrInfo(
            number=pr["number"],
            title=pr["title"],
            author=pr["user"]["login"],
            merged_at=pr["merged_at"],
            reviews=fetch_reviews(pr["number"]),
            check_suites=fetch_check_suites(pr["head"]["sha"])
        )
        all_data.append(info.model_dump(mode="json"))

    with open(output_path, "w") as f:
        json.dump(all_data, f, indent=2)
