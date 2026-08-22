from mcp.server.fastmcp import FastMCP

from github_client import (
    get_pr_files,
    add_comment,
)

from rag import search_repository


# ============================================================
# MCP SERVER
# ============================================================

mcp = FastMCP("github-code-review")


# ============================================================
# TOOL 1: GET PULL REQUEST DIFF
# ============================================================

@mcp.tool()
def get_pull_request_diff(
    installation_token: str,
    repo_name: str,
    pr_number: int,
) -> list:
    """
    Retrieve all files changed in a Pull Request.
    """

    if not installation_token:
        return [{"error": "installation_token is required"}]

    if not repo_name:
        return [{"error": "repo_name is required"}]

    if not pr_number:
        return [{"error": "pr_number is required"}]

    try:
        changes = get_pr_files(
            installation_token=installation_token,
            repo_name=repo_name,
            pr_number=pr_number,
        )

        if changes is None:
            return [
                {
                    "error": "Failed to retrieve Pull Request files"
                }
            ]

        return changes

    except Exception as e:
        return [{"error": str(e)}]


# ============================================================
# TOOL 2: SEARCH REPOSITORY USING RAG
# ============================================================

@mcp.tool()
def search_code(
    query: str,
    top_k: int = 5,
) -> list:
    """
    Search the indexed repository using semantic RAG retrieval.
    """

    if not query or not query.strip():
        return [
            {
                "error": "Search query is required"
            }
        ]

    try:
        results = search_repository(
            query=query,
            top_k=top_k,
        )

        return results

    except Exception as e:
        return [
            {
                "error": str(e)
            }
        ]


# ============================================================
# TOOL 3: GET REPOSITORY FILE
# ============================================================

@mcp.tool()
def get_file(
    installation_token: str,
    repo_name: str,
    file_path: str,
) -> dict:
    """
    Retrieve a file from a GitHub repository.
    """

    if not installation_token:
        return {
            "error": "installation_token is required"
        }

    if not repo_name:
        return {
            "error": "repo_name is required"
        }

    if not file_path:
        return {
            "error": "file_path is required"
        }

    try:
        from github import Github

        github = Github(installation_token)

        try:
            repo = github.get_repo(repo_name)

            file = repo.get_contents(file_path)

            if isinstance(file, list):
                return {
                    "error": "Path points to a directory"
                }

            content = file.decoded_content.decode(
                "utf-8",
                errors="ignore",
            )

            return {
                "file": file_path,
                "content": content,
            }

        finally:
            github.close()

    except Exception as e:
        return {
            "error": str(e)
        }


# ============================================================
# TOOL 4: POST REVIEW COMMENT
# ============================================================

@mcp.tool()
def post_review_comment(
    installation_token: str,
    repo_name: str,
    pr_number: int,
    review: str,
) -> dict:
    """
    Post an AI-generated review comment
    to a GitHub Pull Request.
    """

    if not installation_token:
        return {
            "success": False,
            "error": "installation_token is required"
        }

    if not repo_name:
        return {
            "success": False,
            "error": "repo_name is required"
        }

    if not pr_number:
        return {
            "success": False,
            "error": "pr_number is required"
        }

    if not review or not review.strip():
        return {
            "success": False,
            "error": "Review text is required"
        }

    try:
        success = add_comment(
            installation_token=installation_token,
            repo_name=repo_name,
            pr_number=pr_number,
            review=review,
        )

        return {
            "success": success
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


# ============================================================
# START SERVER
# ============================================================

if __name__ == "__main__":

    print("========================================")
    print("GITHUB CODE REVIEW MCP SERVER")
    print("========================================")
    print("Starting MCP server...")

    mcp.run(
        transport="streamable-http"
    )