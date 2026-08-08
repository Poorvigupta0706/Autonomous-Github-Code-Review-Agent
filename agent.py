from github_client import get_pr_files, add_comment
from graph import create_graph


def run_agent(repo, pr_number):

    files = get_pr_files(repo, pr_number)

    initial_state = {
        "repo": repo,
        "pr_number": pr_number,
        "files": files,
        "bugs": [],
        "security_issues": [],
        "performance_issues": [],
        "final_review": ""
    }

    graph = create_graph()

    result = graph.invoke(initial_state)

    final_review = result["final_review"]

    add_comment(
        repo,
        pr_number,
        final_review
    )

    return final_review


if __name__ == "__main__":

    result = run_agent(
        "Poorvigupta0706/Salescode.Ai",
        1
    )

    print("\nFINAL REVIEW:")
    print(result)