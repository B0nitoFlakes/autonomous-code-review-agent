from fastapi import FastAPI
from pydantic import BaseModel
from reviewer import review_code, review_github

app = FastAPI(title="Autonomous Code Review Agent")

class CodeRequest(BaseModel):
    code: str

class GithubRequest(BaseModel):
    url: str

@app.post("/review/code")
async def review_code_endpoint(request: CodeRequest):
    report = await review_code(request.code)
    return {"report": report}

@app.post("/review/github")
async def review_github_endpoint(request: GithubRequest):
    report = await review_github(request.url)
    return {"report": report}

@app.get("/")
def health_check():
    return {"status": "running"}