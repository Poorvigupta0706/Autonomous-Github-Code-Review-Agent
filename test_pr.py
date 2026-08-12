
import os

from dotenv import load_dotenv
from github import Github


# ============================================================
# LOAD ENVIRONMENT VARIABLES
# ============================================================

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")


# ============================================================
# CHECK TOKEN
# ============================================================

if not GITHUB_TOKEN:
    raise RuntimeError(
        "GITHUB_TOKEN is missing from .env"
    )


# ============================================================
# TEST CONFIGURATION
# ============================================================

REPO_NAME = "Poorvigupta0706/Salescode.Ai"

# CHANGE THIS TO YOUR ACTUAL PR NUMBER
PR_NUMBER = 1


# ============================================================
# GET PULL REQUEST
# ============================================================

print()
print("========================================")
print("GITHUB PR TEST")
print("========================================")

print()
print("Repository:", REPO_NAME)
print("Pull Request:", PR_NUMBER)

print()
print("Connecting to GitHub...")


github = Github(GITHUB_TOKEN)


try:

    repo = github.get_repo(
        REPO_NAME
    )

    print("Repository found successfully.")

    pr = repo.get_pull(
        PR_NUMBER
    )

    print()
    print("========================================")
    print("PULL REQUEST FOUND")
    print("========================================")

    print(
        "PR Number:",
        pr.number
    )

    print(
        "Title:",
        pr.title
    )

    print(
        "State:",
        pr.state
    )

    print(
        "Author:",
        pr.user.login
    )

    print(
        "Base Branch:",
        pr.base.ref
    )

    print(
        "Head Branch:",
        pr.head.ref
    )

    print(
        "URL:",
        pr.html_url
    )

    print()
    print("PR retrieval is working correctly.")


except Exception as e:

    print()
    print("========================================")
    print("PR RETRIEVAL FAILED")
    print("========================================")

    print(
        "Error:",
        e
    )


finally:

    github.close()
