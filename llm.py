import ollama

print("Python started")
print("Calling Ollama...")


def review_code(code):

    response = ollama.chat(
        model="qwen2.5-coder:7b",
        messages=[
            {
                "role": "user",
                "content": f"""
Review this code.

Find:
- bugs
- security issues
- bad practices
- improvements

Code:

{code}
"""
            }
        ]
    )

    print("Ollama responded!")
    return response["message"]["content"]


if __name__ == "__main__":

    result = review_code(
        """
        def login(password):
            return password
        """
    )

    print("Review:")
    print(result)