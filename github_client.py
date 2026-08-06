import os
from github import Github
from dotenv import load_dotenv

load_dotenv()

token = os.getenv("GITHUB_TOKEN")


def get_pr_files(repo_name, pr_number):

    github = Github(token)

    repo = github.get_repo(repo_name)

    pr = repo.get_pull(pr_number)

    files = pr.get_files()

    changes = []

    for file in files:

        changes.append({
            "filename": file.filename,
            "patch": file.patch
        })

    return changes


def add_comment(repo_name, pr_number, review):

    github = Github(token)

    repo = github.get_repo(repo_name)

    pr = repo.get_pull(pr_number)

    pr.create_issue_comment(review)