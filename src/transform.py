import csv
import json
import logging
from pathlib import Path

import config
from schemas.constants import CheckStatus, PrInfo

logger = logging.getLogger(__name__)


def check_code_reviews(reviews: list[dict]) -> bool:
    """Checks if the PR was approved by at least one reviewer."""
    if not reviews:
        return False

    return any(review.get("state", "") == CheckStatus.APPROVED for review in reviews)


def status_checks_passed(check_suites: list[dict]) -> bool:
    return all(
        check.get("status", "").lower() == CheckStatus.COMPLETED and
        check.get("conclusion", "").lower() == CheckStatus.SUCCESS
        for check in check_suites
    )


def run_transform(output_path: Path, input_path: Path) -> None:
    with open(input_path, "r") as input_file:
        data = json.load(input_file)

    pr_list = [PrInfo.model_validate(item) for item in data]

    with open(output_path, "w", newline="", encoding='utf-8') as output_csv:
        writer = csv.writer(output_csv)
        writer.writerow(config.CSV_HEADERS)
        pr_len = len(pr_list)
        for idx, pr in enumerate(pr_list, 1):
            logger.info(f"Processing PR {idx}/{pr_len}, PR#{pr.number}")

            writer.writerow([
                pr.number,
                pr.title,
                pr.author,
                pr.merged_at,
                check_code_reviews(pr.reviews),
                status_checks_passed(pr.check_suites),
            ])
