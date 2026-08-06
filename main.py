from fastapi import FastAPI, Request
from agent import run_agent

app = FastAPI()


@app.post("/webhook")
async def github_webhook(request: Request):

    data = await request.json()

    action = data.get("action")

    if action == "opened":

        repo = data["repository"]["full_name"]

        pr_number = data["number"]

        result = run_agent(repo, pr_number)

        return {
            "status": "review completed",
            "result": result
        }


    return {
        "status":"ignored"
    }