def review_prompt(code):

    return f"""

You are a senior software engineer.

Review this pull request.

Find:

1. Bugs
2. Security problems
3. Performance issues
4. Bad coding practices


Code:

{code}


Give clear suggestions.

"""