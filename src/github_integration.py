from github import Github
from dotenv import load_dotenv
import os

load_dotenv()

g = Github(os.getenv("GITHUB_TOKEN"))

def get_code_from_pr(pr_url: str) -> str:
    parts = pr_url.strip("/").split("/")
    owner = parts[3]
    repo_name = parts[4]
    pr_number = int(parts[6])

    repo = g.get_repo(f"{owner}/{repo_name}")
    pr = repo.get_pull(pr_number)

    code_chunks = []
    for file in pr.get_files():
        if file.patch:
            code_chunks.append(f"# File: {file.filename}\n{file.patch}")

    return "\n\n".join(code_chunks)

def get_code_from_repo(repo_url: str) -> str:
    parts = repo_url.strip("/").split("/")
    owner = parts[3]
    repo_name = parts[4]

    repo = g.get_repo(f"{owner}/{repo_name}")
    contents = repo.get_contents("")

    code_chunks = []
    while contents:
        file_content = contents.pop(0)
        if file_content.type == "dir":
            contents.extend(repo.get_contents(file_content.path))
        else:
            if file_content.path.endswith((".py", ".js", ".ts", ".java", ".go")):
                code_chunks.append(f"# File: {file_content.path}\n{file_content.decoded_content.decode()}")

    return "\n\n".join(code_chunks)

def get_code_from_github(url: str) -> str:
    if "/pull/" in url:
        return get_code_from_pr(url)
    else:
        return get_code_from_repo(url)