from pydantic import BaseModel
from enum import Enum
from datetime import datetime


class PrInfo(BaseModel):
    number: int
    title: str
    author: str
    merged_at: datetime
    reviews: list[dict | None]
    check_suites: list[dict]


class CheckStatus(Enum):
    APPROVED = "APPROVED"
    SUCCESS = "success"
    COMPLETED = "completed"
