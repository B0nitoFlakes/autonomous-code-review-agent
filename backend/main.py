from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from pydantic import BaseModel
from reviewer import review_code, review_github

limiter = Limiter(key_func=get_remote_address)

app = FastAPI(title="Autonomous Code Review Agent")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

active_requests: dict[str, bool] = {}

class CodeRequest(BaseModel):
    code: str

class GithubRequest(BaseModel):
    url: str

def get_ip(request: Request) -> str:
    return request.client.host

@app.post("/review/code")
@limiter.limit("5/minute")
async def review_code_endpoint(request:Request, body: CodeRequest):
    ip = get_ip(request)
    if active_requests.get(ip):
        raise HTTPException(status_code=429, detail="Please wait for your current review to finish before submitting another.")
    
    active_requests[ip] = True
    try:
        result = await review_code(body.code)
        return {
            "report": result["report"],
            "fixed_code": result["fixed_code"]
        }
    finally:
         active_requests.pop(ip, None)

@app.post("/review/github")
@limiter.limit("5/minute")
async def review_github_endpoint(request:Request, body: GithubRequest):
    ip = get_ip(request)
    if active_requests.get(ip):
        raise HTTPException(status_code=429, detail="Please wait for your current review to finish before submitting another.")
    
    active_requests[ip] = True
    try:
        result = await review_github(body.url)
        return {
            "report": result["report"],
            "fixed_code": result["fixed_code"]
        }
    finally:
         active_requests.pop(ip, None)

@app.get("/")
def health_check():
    return {"status": "running"}