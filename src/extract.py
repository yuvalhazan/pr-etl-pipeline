import json
import requests
from tqdm.auto import tqdm
from requests.exceptions import HTTPError, ConnectionError, Timeout

import config


def github_get(
    url: str,
    params: dict = None
) -> dict:
    """Wrapper around requests.get that includes headers and basic error‐handling."""
    try:
        response = requests.get(url, headers=config.HEADERS, params=params, timeout=20)
        response.raise_for_status()
        return response.json()
    except (HTTPError, ConnectionError, Timeout) as e:
        raise e


def paginate_github(url, params=None, per_page=30, page=1):
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


def fetch_merged_prs():
    """
    Fetches all merged pull requests from the repo, filters by closed state, and verifying actual merge status using
    merged_at date.
    return: merged_pr list
    """
    merged_pr = []
    for pr in paginate_github(config.GITHUB_API_PULLS_URL, params={"state": "closed"}):
        if pr.get("merged_at"):
            merged_pr.append(pr)
    return merged_pr


def fetch_reviews(pr_number):
    """
    Fetches all reviews by PR number.
    returns a list of dicts, each is a PR review.
    """
    url = f"{config.GITHUB_API_PULLS_URL}/{pr_number}/reviews"
    return list(paginate_github(url))


def fetch_check_suites(sha):
    """
    Fetches the latest check_suites by the HEAD_SHA of the PR.
    """
    url = f"{config.GITHUB_REPO_URL}/commits/{sha}/check-suites"
    check_suites = next(paginate_github(url=url), {}).get("check_suites", [])
    return check_suites


def run_extract(output_path):
    all_data = []
    for pr in tqdm(fetch_merged_prs(), desc="Extracting merged PR data", ascii="-="):
        pr_info = {
            "number": pr["number"],
            "title": pr["title"],
            "author": pr["user"]["login"],
            "merged_at": pr["merged_at"],
            "reviews": fetch_reviews(pr["number"]),
            "check_suites": fetch_check_suites(pr["head"]["sha"])
        }
        all_data.append(pr_info)
    with open(output_path, "w") as f:
        json.dump(all_data, f, indent=2)
