from typing import Any

from github import Github
from github.PullRequest import PullRequest


def get_pr_files(
    installation_token: str,
    repo_name: str,
    pr_number: int,
) -> list[dict[str, Any]] | None:
    """
    Retrieve all files changed in a GitHub Pull Request.

    Args:
        installation_token:
            GitHub App installation access token.

        repo_name:
            Repository in the format:
            owner/repository

        pr_number:
            Pull Request number.

    Returns:
        A list containing information about each changed file.
        Returns None if the GitHub request fails.
    """

    print()
    print("========================================")
    print("RETRIEVING CHANGED FILES")
    print("========================================")

    github = Github(installation_token)

    try:
        repo = github.get_repo(repo_name)

        pr: PullRequest = repo.get_pull(pr_number)

        changes: list[dict[str, Any]] = []

        for file in pr.get_files():

            change = {
                "filename": file.filename,
                "status": file.status,
                "additions": file.additions,
                "deletions": file.deletions,
                "changes": file.changes,
                "patch": file.patch or "",
            }

            changes.append(change)

            print(
                f"File: {file.filename} | "
                f"Status: {file.status} | "
                f"+{file.additions} "
                f"-{file.deletions}"
            )

        print()
        print(
            "Total changed files:",
            len(changes),
        )

        print(
            "Changed files retrieved successfully"
        )

        return changes

    except Exception as e:

        print(
            "Failed to retrieve changed files"
        )

        print(
            "Error:",
            e,
        )

        return None

    finally:
        github.close()


def get_file_content(
    installation_token: str,
    repo_name: str,
    file_path: str,
    ref: str | None = None,
) -> dict[str, Any]:
    """
    Retrieve the contents of a repository file.

    Args:
        installation_token:
            GitHub App installation access token.

        repo_name:
            Repository in owner/repository format.

        file_path:
            Path of the file inside the repository.

        ref:
            Git branch, tag, or commit SHA.
            If omitted, GitHub uses the default branch.

    Returns:
        Dictionary containing file path and content.
    """

    github = Github(installation_token)

    try:

        repo = github.get_repo(repo_name)

        file = repo.get_contents(
            file_path,
            ref=ref,
        )

        if isinstance(file, list):
            return {
                "success": False,
                "error": "Path points to a directory",
            }

        content = file.decoded_content.decode(
            "utf-8",
            errors="ignore",
        )

        return {
            "success": True,
            "file": file_path,
            "content": content,
        }

    except Exception as e:

        return {
            "success": False,
            "error": str(e),
        }

    finally:
        github.close()


def add_comment(
    installation_token: str,
    repo_name: str,
    pr_number: int,
    review: str,
) -> bool:
    """
    Post the AI-generated review as a general
    Pull Request comment.

    This is NOT an inline review comment yet.
    """

    print()
    print("========================================")
    print("POSTING AI REVIEW")
    print("========================================")

    if not review.strip():

        print("Review is empty.")

        return False

    github = Github(installation_token)

    try:

        repo = github.get_repo(repo_name)

        pr = repo.get_pull(pr_number)

        pr.create_issue_comment(
            review
        )

        print(
            "AI review comment posted successfully"
        )

        return True

    except Exception as e:

        print(
            "Failed to post AI review"
        )

        print(
            "Error:",
            e,
        )

        return False

    finally:
        github.close()