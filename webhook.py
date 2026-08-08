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
        hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(signature, expected)


@app.route("/webhook", methods=["POST"])
def github_webhook():

    payload = request.get_data()

    signature = request.headers.get("X-Hub-Signature-256")

    if not verify_signature(signature, payload):
        return jsonify({"error": "Invalid signature"}), 401

    event = request.headers.get("X-GitHub-Event")

    print("GitHub event:", event)

    if event != "pull_request":
        return jsonify({"message": "Event ignored"}), 200

    data = request.get_json()

    action = data.get("action")

    if action not in ["opened", "synchronize", "reopened"]:
        return jsonify({"message": "Action ignored"}), 200

    repo = data["repository"]["full_name"]
    pr_number = data["pull_request"]["number"]

    print("Pull Request received")
    print("Repository:", repo)
    print("PR number:", pr_number)
    print("Action:", action)

    try:

        result = run_agent(repo, pr_number)

        print("Review completed")

        return jsonify({
            "message": "Review completed",
            "repository": repo,
            "pr_number": pr_number
        }), 200

    except Exception as e:

        print("Review failed:", e)

        return jsonify({
            "error": str(e)
        }), 500


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000
    )