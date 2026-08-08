import os
import time

import jwt
import requests

GITHUB_API = "https://api.github.com"


def create_app_jwt():
    app_id = os.environ["GITHUB_APP_ID"]
    private_key_path = os.environ["GITHUB_PRIVATE_KEY_PATH"]

    with open(private_key_path, "r") as f:
        private_key = f.read()

    now = int(time.time())

    payload = {
        "iat": now - 60,
        "exp": now + (10 * 60),
        "iss": app_id,
    }

    return jwt.encode(
        payload,
        private_key,
        algorithm="RS256",
    )


def get_installation_token(installation_id):
    app_jwt = create_app_jwt()

    headers = {
        "Authorization": f"Bearer {app_jwt}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }

    response = requests.post(
        f"{GITHUB_API}/app/installations/{installation_id}/access_tokens",
        headers=headers,
        timeout=30,
    )

    response.raise_for_status()

    return response.json()["token"]