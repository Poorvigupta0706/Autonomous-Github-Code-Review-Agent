from llm import review_code
from state import ReviewState


def bug_agent(state: ReviewState):

    all_bugs = []

    for file in state["files"]:

        filename = file["filename"]
        patch = file["patch"]

        bug_prompt = f"""
You are a bug detection agent.

Analyze this GitHub code change only for bugs.

File:
{filename}

Code:
{patch}

Find:
- logical bugs
- null pointer problems
- incorrect conditions
- runtime errors
- edge cases

If there are no bugs, say:
No bugs found.
"""

        bug_result = review_code(bug_prompt)

        all_bugs.append({
            "file": filename,
            "result": bug_result
        })

    return {
        "bugs": all_bugs
    }


def security_agent(state: ReviewState):

    all_security = []

    for file in state["files"]:

        filename = file["filename"]
        patch = file["patch"]

        security_prompt = f"""
You are a security code review agent.

Analyze this GitHub code change only for security problems.

File:
{filename}

Code:
{patch}

Find:
- hardcoded secrets
- SQL injection
- authentication problems
- authorization problems
- unsafe input
- insecure data handling

If there are no security issues, say:
No security issues found.
"""

        security_result = review_code(security_prompt)

        all_security.append({
            "file": filename,
            "result": security_result
        })

    return {
        "security_issues": all_security
    }


def performance_agent(state: ReviewState):

    all_performance = []

    for file in state["files"]:

        filename = file["filename"]
        patch = file["patch"]

        performance_prompt = f"""
You are a performance code review agent.

Analyze this GitHub code change only for performance problems.

File:
{filename}

Code:
{patch}

Find:
- unnecessary loops
- O(n²) or worse algorithms
- unnecessary database calls
- unnecessary memory usage
- inefficient operations

If there are no performance issues, say:
No performance issues found.
"""

        performance_result = review_code(performance_prompt)

        all_performance.append({
            "file": filename,
            "result": performance_result
        })

    return {
        "performance_issues": all_performance
    }


def final_agent(state: ReviewState):

    final_prompt = f"""
You are the final code review agent.

Create a clear GitHub Pull Request review.

BUGS:
{state["bugs"]}

SECURITY ISSUES:
{state["security_issues"]}

PERFORMANCE ISSUES:
{state["performance_issues"]}

Create one final review.

For each important issue include:

- Severity
- File
- Problem
- Explanation
- Suggested fix

Remove duplicate issues.

Do not invent problems.

If there are no important issues, say:

No significant issues found.
"""

    final_review = review_code(final_prompt)

    return {
        "final_review": final_review
    }