from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from pydantic import BaseModel
from reviewer import review_code, review_github, review_file

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

file_cache: dict[str, dict] = {}
active_requests: dict[str, bool] = {}

class CodeRequest(BaseModel):
    code: str

class GithubRequest(BaseModel):
    url: str

class FileRequest(BaseModel):
    filename: str
    code:str

def get_ip(request: Request) -> str:
    return request.client.host

@app.post("/review/code")
@limiter.limit("2/minute")
async def review_code_endpoint(request:Request, body: CodeRequest):
    ip = get_ip(request)
    if active_requests.get(ip):
        raise HTTPException(status_code=429, detail="Please wait for your current review to finish before submitting another.")
    
    active_requests[ip] = True
    try:
        result = await review_code(body.code)
        return result
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))
    finally:
         active_requests.pop(ip, None)

@app.post("/review/github")
@limiter.limit("5/minute")
async def review_github_endpoint(request: Request, body: GithubRequest):
    ip = get_ip(request)
    keys_to_delete = [k for k in file_cache if k.startswith(ip + ":")]
    for key in keys_to_delete:
        file_cache.pop(key, None)
    try:
        result = await review_github(body.url)
        return result
    except Exception as e :
        print(e)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/review/file")
@limiter.limit("2/minute")
async def review_file_endpoint(request:Request, body: FileRequest):
    ip = get_ip(request)
    cache_key = ip + ":" + body.filename

    if active_requests.get(ip):
        raise HTTPException(status_code=429, detail="Please wait for your current review to finish before submitting another.")
    
    if file_cache.get(cache_key):
        return file_cache[cache_key]
    
    active_requests[ip] = True

    try:   
        result = await review_file(body.filename, body.code)
        file_cache[cache_key] = result
        return result
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        active_requests.pop(ip, None)



@app.get("/")
def health_check():
    return {"status": "running"}