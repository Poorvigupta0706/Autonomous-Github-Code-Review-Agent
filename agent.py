from github_client import get_pr_files, add_comment
from graph import create_graph


def run_agent(repo, pr_number):
    print("=" * 60)
    print("AUTONOMOUS GITHUB CODE REVIEW AGENT")
    print("=" * 60)

    print(f"Repository : {repo}")
    print(f"Pull Request : #{pr_number}")
    print()

    print("Fetching pull request files...")

    files = get_pr_files(repo, pr_number)

    if not files:
        print("No files found in this pull request.")
        return "No files found in this pull request."

    print(f"Found {len(files)} file(s).")
    print()

    initial_state = {
        "repo": repo,
        "pr_number": pr_number,
        "files": files,
        "bugs": [],
        "security_issues": [],
        "performance_issues": [],
        "final_review": "",
    }

    print("Starting review agents...")
    print()

    graph = create_graph()

    result = graph.invoke(initial_state)

    final_review = result.get("final_review", "")

    if not final_review:
        final_review = "No significant issues found."

    print("=" * 60)
    print("FINAL REVIEW")
    print("=" * 60)
    print(final_review)
    print()

    print("Posting review to GitHub...")

    add_comment(
        repo,
        pr_number,
        final_review
    )

    print("Review posted successfully.")

    return final_review


def main():
    print()
    print("=" * 60)
    print("AUTONOMOUS GITHUB CODE REVIEW AGENT")
    print("=" * 60)
    print()

    repo = input(
        "Enter GitHub repository (owner/repository): "
    ).strip()

    pr_number = input(
        "Enter Pull Request number: "
    ).strip()

    if not repo:
        print("Repository cannot be empty.")
        return

    if "/" not in repo:
        print(
            "Invalid repository format.\n"
            "Use: owner/repository\n"
            "Example: octocat/Hello-World"
        )
        return

    try:
        pr_number = int(pr_number)
    except ValueError:
        print("PR number must be a number.")
        return

    if pr_number <= 0:
        print("PR number must be greater than 0.")
        return

    run_agent(repo, pr_number)


if __name__ == "__main__":
    main()