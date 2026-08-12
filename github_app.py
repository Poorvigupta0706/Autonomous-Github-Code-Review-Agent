import os
import time
import hmac
import hashlib
from pathlib import Path

import jwt
import requests

from dotenv import load_dotenv
from flask import Flask, request, jsonify

from github_client import get_pr_files, add_comment


# ============================================================
# LOAD ENVIRONMENT VARIABLES
# ============================================================

load_dotenv()


# ============================================================
# FLASK APPLICATION
# ============================================================

app = Flask(__name__)


# ============================================================
# CONFIGURATION
# ============================================================

GITHUB_APP_ID = os.getenv("GITHUB_APP_ID")
GITHUB_PRIVATE_KEY_PATH = os.getenv(
    "GITHUB_PRIVATE_KEY_PATH"
)
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET")


# ============================================================
# VALIDATE ENVIRONMENT VARIABLES
# ============================================================

if not GITHUB_APP_ID:
    raise RuntimeError(
        "GITHUB_APP_ID environment variable is missing"
    )


if not GITHUB_PRIVATE_KEY_PATH:
    raise RuntimeError(
        "GITHUB_PRIVATE_KEY_PATH environment variable is missing"
    )


if not WEBHOOK_SECRET:
    raise RuntimeError(
        "WEBHOOK_SECRET environment variable is missing"
    )


# ============================================================
# LOAD GITHUB PRIVATE KEY
# ============================================================

private_key_path = Path(
    GITHUB_PRIVATE_KEY_PATH
)


if not private_key_path.exists():
    raise RuntimeError(
        f"GitHub private key file not found: "
        f"{private_key_path}"
    )


try:

    GITHUB_PRIVATE_KEY = private_key_path.read_text()

except Exception as e:

    raise RuntimeError(
        f"Could not read GitHub private key: {e}"
    )


# ============================================================
# CONVERT APP ID TO INTEGER
# ============================================================

try:

    GITHUB_APP_ID = int(GITHUB_APP_ID)

except ValueError:

    raise RuntimeError(
        "GITHUB_APP_ID must be an integer"
    )


# ============================================================
# WEBHOOK SIGNATURE VERIFICATION
# ============================================================

def verify_webhook_signature(
    payload_body,
    signature
):
    """
    Verify that the webhook request actually came from GitHub.
    """

    if not signature:

        print("No webhook signature received")

        return False


    if not signature.startswith("sha256="):

        print("Invalid webhook signature format")

        return False


    expected_signature = hmac.new(
        WEBHOOK_SECRET.encode("utf-8"),
        payload_body,
        hashlib.sha256
    ).hexdigest()


    expected_signature = (
        "sha256=" + expected_signature
    )


    return hmac.compare_digest(
        expected_signature,
        signature
    )


# ============================================================
# CREATE GITHUB APP JWT
# ============================================================

def create_github_app_jwt():
    """
    Create a JWT that authenticates the GitHub App itself.
    """

    now = int(time.time())


    payload = {
        "iat": now - 60,
        "exp": now + (10 * 60),
        "iss": GITHUB_APP_ID
    }


    token = jwt.encode(
        payload,
        GITHUB_PRIVATE_KEY,
        algorithm="RS256"
    )


    return token


# ============================================================
# GET INSTALLATION ACCESS TOKEN
# ============================================================

def get_installation_access_token(
    installation_id
):
    """
    Exchange the GitHub App JWT for an
    installation access token.
    """

    print()
    print("========================================")
    print("GITHUB APP AUTHENTICATION")
    print("========================================")


    print("Creating GitHub App JWT...")


    app_jwt = create_github_app_jwt()


    url = (
        "https://api.github.com/app/installations/"
        f"{installation_id}/access_tokens"
    )


    headers = {
        "Authorization": f"Bearer {app_jwt}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28"
    }


    print(
        "Requesting installation access token..."
    )


    try:

        response = requests.post(
            url,
            headers=headers,
            timeout=30
        )

    except requests.RequestException as e:

        print(
            "GitHub API request failed:",
            e
        )

        return None


    if response.status_code != 201:

        print(
            "Failed to get installation access token"
        )

        print(
            "Status:",
            response.status_code
        )

        print(
            "Response:",
            response.text
        )

        return None


    data = response.json()


    installation_token = data.get("token")


    if not installation_token:

        print(
            "GitHub did not return "
            "an installation token"
        )

        return None


    print(
        "Installation access token "
        "obtained successfully"
    )


    return installation_token


# ============================================================
# RETRIEVE PULL REQUEST
# ============================================================

def retrieve_pr(
    installation_token,
    owner,
    repo,
    pr_number
):
    """
    Retrieve the complete Pull Request
    object from GitHub.
    """

    print()
    print("========================================")
    print("RETRIEVING PULL REQUEST")
    print("========================================")


    url = (
        f"https://api.github.com/repos/"
        f"{owner}/{repo}/pulls/{pr_number}"
    )


    headers = {
        "Authorization": (
            f"Bearer {installation_token}"
        ),
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28"
    }


    print(
        "GitHub API URL:",
        url
    )


    try:

        response = requests.get(
            url,
            headers=headers,
            timeout=30
        )

    except requests.RequestException as e:

        print(
            "GitHub API request failed:",
            e
        )

        return None


    if response.status_code != 200:

        print(
            "Failed to retrieve Pull Request"
        )

        print(
            "Status:",
            response.status_code
        )

        print(
            "Response:",
            response.text
        )

        return None


    pr = response.json()


    print()
    print("PR RETRIEVED SUCCESSFULLY")
    print("----------------------------------------")

    print(
        "PR number:",
        pr.get("number")
    )

    print(
        "Title:",
        pr.get("title")
    )

    print(
        "State:",
        pr.get("state")
    )

    print(
        "Draft:",
        pr.get("draft")
    )

    print(
        "Author:",
        pr.get("user", {}).get("login")
    )

    print(
        "Base branch:",
        pr.get("base", {}).get("ref")
    )

    print(
        "Head branch:",
        pr.get("head", {}).get("ref")
    )

    print(
        "Created:",
        pr.get("created_at")
    )

    print(
        "Updated:",
        pr.get("updated_at")
    )

    print("----------------------------------------")


    return pr


# ============================================================
# MAIN AI REVIEW PIPELINE
# ============================================================

def start_ai_code_review(
    payload
):
    """
    Main AI code review pipeline.

    Current stages:

    1. Authenticate GitHub App
    2. Retrieve Pull Request
    3. Retrieve changed files
    4. AI review will be added later
    5. Post review will be added later
    """

    print()
    print("========================================")
    print("STARTING AI CODE REVIEW")
    print("========================================")


    # --------------------------------------------------------
    # GET REPOSITORY INFORMATION
    # --------------------------------------------------------

    repository = payload.get(
        "repository",
        {}
    )


    owner = repository.get(
        "owner",
        {}
    ).get("login")


    repo = repository.get("name")


    pr_number = payload.get("number")


    installation = payload.get(
        "installation",
        {}
    )


    installation_id = installation.get("id")


    # --------------------------------------------------------
    # VALIDATE WEBHOOK DATA
    # --------------------------------------------------------

    if not owner:

        print(
            "ERROR: Repository owner not found"
        )

        return False


    if not repo:

        print(
            "ERROR: Repository name not found"
        )

        return False


    if not pr_number:

        print(
            "ERROR: Pull Request number not found"
        )

        return False


    if not installation_id:

        print(
            "ERROR: Installation ID not found"
        )

        return False


    repo_name = f"{owner}/{repo}"


    print()
    print(
        "Repository:",
        repo_name
    )

    print(
        "Pull Request:",
        pr_number
    )

    print(
        "Installation ID:",
        installation_id
    )


    # --------------------------------------------------------
    # STEP 1: GITHUB APP AUTHENTICATION
    # --------------------------------------------------------

    print()
    print(
        "STEP 1: GitHub App authentication"
    )


    installation_token = (
        get_installation_access_token(
            installation_id
        )
    )


    if not installation_token:

        print(
            "ERROR: Could not authenticate "
            "GitHub App"
        )

        return False


    # --------------------------------------------------------
    # STEP 2: RETRIEVE PULL REQUEST
    # --------------------------------------------------------

    print()
    print(
        "STEP 2: Retrieve Pull Request"
    )


    pr = retrieve_pr(
        installation_token=installation_token,
        owner=owner,
        repo=repo,
        pr_number=pr_number
    )


    if not pr:

        print(
            "ERROR: Could not retrieve "
            "Pull Request"
        )

        return False


    # --------------------------------------------------------
    # STEP 3: RETRIEVE CHANGED FILES
    # --------------------------------------------------------

    print()
    print(
        "STEP 3: Retrieve changed files"
    )


    changes = get_pr_files(
        installation_token=installation_token,
        repo_name=repo_name,
        pr_number=pr_number
    )


    if changes is None:

        print(
            "ERROR: Could not retrieve "
            "changed files"
        )

        return False


    print()
    print(
        "Changed files retrieved:",
        len(changes)
    )


    # --------------------------------------------------------
    # DISPLAY FILES
    # --------------------------------------------------------

    for change in changes:

        print(
            f"- {change['filename']} "
            f"({change['status']})"
        )


    # --------------------------------------------------------
    # STEP 4: AI REVIEW
    # --------------------------------------------------------
    #
    # This is where you will later add:
    #
    # MCP
    # RAG
    # Ollama
    # Code analysis
    #
    # Example:
    #
    # review = run_ai_review(changes)
    #
    # --------------------------------------------------------

    print()
    print(
        "STEP 4: AI review not implemented yet"
    )


    # --------------------------------------------------------
    # STEP 5: POST REVIEW
    # --------------------------------------------------------
    #
    # Later:
    #
    # review = "AI review result..."
    #
    # add_comment(
    #     installation_token,
    #     repo_name,
    #     pr_number,
    #     review
    # )
    #
    # --------------------------------------------------------


    print()
    print("========================================")
    print("PR RETRIEVAL COMPLETE")
    print("========================================")


    return True


# ============================================================
# GITHUB WEBHOOK
# ============================================================

@app.route(
    "/webhook",
    methods=["POST"]
)
def github_webhook():

    print()
    print("========================================")
    print("WEBHOOK FUNCTION CALLED")
    print("========================================")


    # --------------------------------------------------------
    # GET RAW REQUEST BODY
    # --------------------------------------------------------

    payload_body = request.get_data()


    print(
        "Payload received:",
        len(payload_body),
        "bytes"
    )


    # --------------------------------------------------------
    # GET SIGNATURE
    # --------------------------------------------------------

    signature = request.headers.get(
        "X-Hub-Signature-256"
    )


    print(
        "Signature received:",
        bool(signature)
    )


    # --------------------------------------------------------
    # VERIFY WEBHOOK SIGNATURE
    # --------------------------------------------------------

    if not verify_webhook_signature(
        payload_body,
        signature
    ):

        print(
            "Webhook signature verification FAILED"
        )

        return jsonify({
            "error": "Invalid signature"
        }), 401


    print(
        "Webhook signature verified"
    )


    # --------------------------------------------------------
    # READ EVENT TYPE
    # --------------------------------------------------------

    event = request.headers.get(
        "X-GitHub-Event"
    )


    print(
        "GitHub event:",
        event
    )


    # --------------------------------------------------------
    # PARSE JSON
    # --------------------------------------------------------

    payload = request.get_json(
        silent=True
    )


    if payload is None:

        print(
            "Could not parse JSON payload"
        )

        return jsonify({
            "error": "Invalid JSON"
        }), 400


    # --------------------------------------------------------
    # PULL REQUEST EVENT
    # --------------------------------------------------------

    if event == "pull_request":

        action = payload.get("action")


        repository = payload.get(
            "repository",
            {}
        )


        owner = repository.get(
            "owner",
            {}
        ).get("login")


        repo = repository.get("name")


        pr_number = payload.get("number")


        print(
            "Pull request action:",
            action
        )


        print(
            "Repository:",
            f"{owner}/{repo}"
        )


        print(
            "Pull request:",
            pr_number
        )


        # ----------------------------------------------------
        # ALLOWED ACTIONS
        # ----------------------------------------------------

        allowed_actions = {
            "opened",
            "synchronize",
            "reopened"
        }


        if action not in allowed_actions:

            print(
                "Ignoring pull request action:",
                action
            )

            return jsonify({
                "message": "Event ignored"
            }), 200


        # ----------------------------------------------------
        # START REVIEW
        # ----------------------------------------------------

        success = start_ai_code_review(
            payload
        )


        if not success:

            return jsonify({
                "error": "AI code review failed"
            }), 500


        return jsonify({
            "message": (
                "PR retrieved and "
                "changed files retrieved successfully"
            )
        }), 200


    # --------------------------------------------------------
    # IGNORE OTHER EVENTS
    # --------------------------------------------------------

    print(
        "Ignoring GitHub event:",
        event
    )


    return jsonify({
        "message": "Event ignored"
    }), 200


# ============================================================
# HEALTH CHECK
# ============================================================

@app.route(
    "/",
    methods=["GET"]
)
def health_check():

    return jsonify({
        "status": "running",
        "service": (
            "Autonomous GitHub "
            "Code Review Agent"
        )
    })


# ============================================================
# RUN SERVER
# ============================================================

if __name__ == "__main__":

    print()
    print("========================================")
    print("AUTONOMOUS GITHUB CODE REVIEW AGENT")
    print("========================================")

    print(
        "Starting webhook server..."
    )

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False
    )
