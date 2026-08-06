from typing import TypedDict


class ReviewState(TypedDict):

    repo: str
    pr_number: int
    files: list

    bugs: list
    security_issues: list
    performance_issues: list

    final_review: str