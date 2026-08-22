import os
import asyncio

from dotenv import load_dotenv

from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client


# ============================================================
# CONFIGURATION
# ============================================================

load_dotenv()

MCP_SERVER_URL = "http://127.0.0.1:8000/mcp"


# ============================================================
# GET USER INPUT
# ============================================================

def get_user_input():

    print()
    print("=" * 60)
    print("GITHUB PULL REQUEST CONFIGURATION")
    print("=" * 60)

    repo_name = input(
        "Enter GitHub repository (owner/repository): "
    ).strip()

    while not repo_name:
        print("Repository cannot be empty.")
        repo_name = input(
            "Enter GitHub repository (owner/repository): "
        ).strip()

    pr_number_input = input(
        "Enter Pull Request number: "
    ).strip()

    while not pr_number_input.isdigit():
        print("PR number must be a number.")

        pr_number_input = input(
            "Enter Pull Request number: "
        ).strip()

    pr_number = int(pr_number_input)

    return repo_name, pr_number


# ============================================================
# MAIN
# ============================================================

async def main():

    print()
    print("=" * 60)
    print("AUTONOMOUS GITHUB CODE REVIEW AGENT")
    print("=" * 60)

    # --------------------------------------------------------
    # Load GitHub token
    # --------------------------------------------------------

    github_token = os.getenv("GITHUB_TOKEN")

    if not github_token:
        raise RuntimeError(
            "GITHUB_TOKEN is missing from .env"
        )

    # --------------------------------------------------------
    # Ask user for repository and PR
    # --------------------------------------------------------

    repo_name, pr_number = get_user_input()

    print()
    print("=" * 60)
    print("REVIEW CONFIGURATION")
    print("=" * 60)

    print(f"Repository : {repo_name}")
    print(f"Pull Request : #{pr_number}")

    # --------------------------------------------------------
    # Connect to MCP server
    # --------------------------------------------------------

    print()
    print("Connecting to MCP server...")
    print(f"Server: {MCP_SERVER_URL}")

    async with streamablehttp_client(
        MCP_SERVER_URL
    ) as (
        read_stream,
        write_stream,
        _,
    ):

        async with ClientSession(
            read_stream,
            write_stream,
        ) as session:

            # ------------------------------------------------
            # Initialize MCP
            # ------------------------------------------------

            await session.initialize()

            print("Connected to MCP server")

            # ------------------------------------------------
            # List tools
            # ------------------------------------------------

            tools = await session.list_tools()

            print()
            print("Available MCP tools:")

            for tool in tools.tools:
                print(f"  - {tool.name}")

            # ------------------------------------------------
            # STEP 1: GET PR DIFF
            # ------------------------------------------------

            print()
            print("=" * 60)
            print("STEP 1: RETRIEVING PULL REQUEST DIFF")
            print("=" * 60)

            diff_result = await session.call_tool(
                "get_pull_request_diff",
                arguments={
                    "installation_token": github_token,
                    "repo_name": repo_name,
                    "pr_number": pr_number,
                },
            )

            print("Pull Request diff retrieved successfully.")

            print()
            print("Diff result:")

            print(diff_result)

    print()
    print("=" * 60)
    print("PR DIFF STEP COMPLETED")
    print("=" * 60)


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    asyncio.run(main())