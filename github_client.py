from github import Github


def get_pr_files(
    installation_token,
    repo_name,
    pr_number
):
    """
    Retrieve all changed files from a Pull Request.

    Args:
        installation_token: GitHub App installation access token.
        repo_name: Repository name in the format 'owner/repository'.
        pr_number: Pull Request number.

    Returns:
        List of dictionaries containing file information,
        or None if retrieval fails.
    """

    print()
    print("========================================")
    print("RETRIEVING CHANGED FILES")
    print("========================================")

    github = Github(installation_token)

    try:
        repo = github.get_repo(repo_name)
        pr = repo.get_pull(pr_number)
        files = pr.get_files()

        changes = []

        for file in files:
            changes.append({
                "filename": file.filename,
                "status": file.status,
                "additions": file.additions,
                "deletions": file.deletions,
                "changes": file.changes,
                "patch": file.patch,
            })

            print(
                f"File: {file.filename} | "
                f"Status: {file.status} | "
                f"+{file.additions} "
                f"-{file.deletions}"
            )

        print()
        print("Total changed files:", len(changes))
        print("Changed files retrieved successfully")

        return changes

    except Exception as e:
        print("Failed to retrieve changed files")
        print("Error:", e)
        return None

    finally:
        github.close()


def add_comment(
    installation_token,
    repo_name,
    pr_number,
    review
):
    """
    Add a general comment to a Pull Request.

    Args:
        installation_token: GitHub App installation access token.
        repo_name: Repository name in the format 'owner/repository'.
        pr_number: Pull Request number.
        review: Review text to post.

    Returns:
        True if successful, otherwise False.
    """

    print()
    print("========================================")
    print("POSTING AI REVIEW")
    print("========================================")

    github = Github(installation_token)

    try:
        repo = github.get_repo(repo_name)
        pr = repo.get_pull(pr_number)

        pr.create_issue_comment(review)

        print("AI review comment posted successfully")

        return True

    except Exception as e:
        print("Failed to post AI review")
        print("Error:", e)
        return False

    finally:
        github.close()