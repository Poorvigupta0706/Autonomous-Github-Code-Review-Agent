import json
import requests


OLLAMA_URL = "http://127.0.0.1:11434/api/generate"
MODEL = "qwen2.5-coder:7b"


def generate_review(
    code: str,
    context: str = "",
) -> str:

    prompt = f"""
You are an expert software engineer performing a Pull Request code review.

Analyze the changed code using the repository context.

Focus ONLY on real and important issues:

1. Bugs
2. Logic errors
3. Security vulnerabilities
4. Performance problems
5. Error handling
6. Maintainability
7. Incorrect API usage
8. Important edge cases

Do NOT invent problems.

Repository context:
-------------------
{context}
-------------------

Pull Request changes:
---------------------
{code}
---------------------

For every important issue, use:

Severity: HIGH / MEDIUM / LOW
File:
Location:
Problem:
Why it matters:
Suggested fix:

If there are no significant issues, return exactly:

No significant issues found.
"""

    print()
    print("========================================")
    print("OLLAMA CODE REVIEW")
    print("========================================")
    print(f"Model: {MODEL}")
    print("Generating review...")
    print()

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL,
            "prompt": prompt,
            "stream": True,
            "keep_alive": "10m",
            "options": {
                "temperature": 0.2,
                "num_predict": 1024,
            },
        },
        stream=True,
        timeout=(30, 600),
    )

    response.raise_for_status()

    review_parts = []

    print("----------------------------------------")

    for line in response.iter_lines():

        if not line:
            continue

        data = json.loads(line)

        chunk = data.get("response", "")

        if chunk:
            print(chunk, end="", flush=True)
            review_parts.append(chunk)

        if data.get("done"):
            break

    print()
    print("----------------------------------------")

    return "".join(review_parts).strip()