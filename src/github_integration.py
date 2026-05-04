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
    print(f"Fetching code from PR {pr_number} in {repo_name} owned by {owner}")

    repo = g.get_repo(f"{owner}/{repo_name}")
    pr = repo.get_pull(pr_number)
    
    code_chunks = []
    for file in pr.get_files():
        if file.patch:
            code_chunks.append(f"# File: {file.filename}\n{file.patch}\n")
    
    return "\n\n".join(code_chunks)

if __name__ == "__main__":
    pr_url = "https://github.com/hello/comar/pull/1234"
    code = get_code_from_pr(pr_url)
    print(code)
