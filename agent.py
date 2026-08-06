from github_client import get_pr_files, add_comment
from llm import review_code


def run_agent(repo, pr_number):

    files = get_pr_files(repo, pr_number)

    all_bugs = ""
    all_security = ""
    all_performance = ""

    for file in files:

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

        all_bugs += f"""
## {filename}

{bug_result}

"""

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

        all_security += f"""
## {filename}

{security_result}

"""

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

        all_performance += f"""
## {filename}

{performance_result}

"""

    final_prompt = f"""
You are the final code review agent.

Create a clear GitHub Pull Request review.

BUGS:
{all_bugs}

SECURITY ISSUES:
{all_security}

PERFORMANCE ISSUES:
{all_performance}

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

    add_comment(
        repo,
        pr_number,
        final_review
    )

    return final_review