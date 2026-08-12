import os
import hmac
import hashlib

from flask import Flask, jsonify, request

from agent import run_agent


app = Flask(__name__)

WEBHOOK_SECRET = os.environ["WEBHOOK_SECRET"]


def verify_signature(signature, payload):
    if not signature:
        return False

    expected = "sha256=" + hmac.new(
        WEBHOOK_SECRET.encode("utf-8"),
        payload,
        hashlib.sha256,
    ).hexdigest()

    return hmac.compare_digest(signature, expected)


@app.route("/webhook", methods=["POST"])
def github_webhook():

    print("\n" + "=" * 60)
    print("WEBHOOK FUNCTION CALLED")
    print("=" * 60)

    payload = request.get_data()

    print("Payload received:", len(payload), "bytes")

    signature = request.headers.get("X-Hub-Signature-256")

    print("Signature received:", bool(signature))

    if not verify_signature(signature, payload):
        print("INVALID WEBHOOK SIGNATURE")
        return jsonify({"error": "Invalid signature"}), 401

    print("Webhook signature verified")

    event = request.headers.get("X-GitHub-Event")

    print("GitHub event:", event)

    if event != "pull_request":
        print("Event ignored:", event)
        return jsonify({"message": "Event ignored"}), 200

    data = request.get_json(silent=True)

    if not data:
        print("Could not parse JSON payload")
        return jsonify({"error": "Invalid JSON"}), 400

    action = data.get("action")

    print("Pull request action:", action)

    if action not in ["opened", "synchronize", "reopened"]:
        print("Pull request action ignored:", action)
        return jsonify({"message": "Action ignored"}), 200

    repository = data.get("repository", {})
    pull_request = data.get("pull_request", {})

    repo = repository.get("full_name")
    pr_number = pull_request.get("number")

    installation = data.get("installation", {})
    installation_id = installation.get("id")

    print("Repository:", repo)
    print("Pull request:", pr_number)
    print("Installation ID:", installation_id)

    if not repo or not pr_number:
        print("Missing repository or pull request number")
        return jsonify({"error": "Invalid pull request payload"}), 400

    try:
        print("Starting AI code review...")

        result = run_agent(repo, pr_number)

        print("AI code review finished")
        print("Agent result:", result)

        return jsonify(
            {
                "message": "Review completed",
                "repository": repo,
                "pr_number": pr_number,
            }
        ), 200

    except Exception as e:
        print("Review failed:", repr(e))

        return jsonify(
            {
                "error": str(e),
                "repository": repo,
                "pr_number": pr_number,
            }
        ), 500


@app.route("/", methods=["GET"])
def home():
    return jsonify(
        {
            "status": "running",
            "service": "Autonomous GitHub Code Review Agent",
        }
    ), 200


if __name__ == "__main__":
    print("Python started")
    print("Calling Ollama...")
    print("Starting Flask webhook server...")

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False,
    )