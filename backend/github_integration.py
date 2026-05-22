from github import Github
from dotenv import load_dotenv
from collections import deque
import os

load_dotenv()

g = Github(os.getenv("GITHUB_TOKEN"))

MAX_FILES = 20
MAX_FILE_SIZE = 50000
MAX_TOTAL_SIZE = 100000
MAX_DIRECTORY_DEPTH = 5

ALLOWED_EXTENSIONS = (
    ".py",
    ".js",
    ".ts",
    ".jsx",
    ".tsx",
    ".html",
    ".css",
    ".sql",
    ".java",
    ".go",
    ".c",
    ".cpp",
    ".h",
    ".hpp",
    ".cs",
)

SKIP_DIRECTORIES = {
    "node_modules",
    "dist",
    "build",
    ".git",
    "__pycache__",
    "coverage",
    "vendor",
    ".next",
    "out",
}

def should_skip_path(path: str) -> bool:
    parts = path.split("/")

    return any(part in SKIP_DIRECTORIES for part in parts)

def get_code_from_pr(pr_url: str) -> str:
    parts = pr_url.strip("/").split("/")

    if len(parts) < 7:
        raise ValueError("Invalid PR URL format.")

    owner = parts[3]
    repo_name = parts[4]
    pr_number = int(parts[6])

    repo = g.get_repo(f"{owner}/{repo_name}")
    pr = repo.get_pull(pr_number)

    code_chunks = []
    total_size = 0

    for file in pr.get_files():

        if len(code_chunks) >= MAX_FILES:
            code_chunks.append(
                f"# Note: Review limited to first {MAX_FILES} files."
            )
            break

        if not file.patch:
            continue

        if should_skip_path(file.filename):
            continue

        if not file.filename.endswith(ALLOWED_EXTENSIONS):
            continue

        patch = file.patch

        if len(patch) > MAX_FILE_SIZE:
            patch = (
                patch[:MAX_FILE_SIZE]
                + "\n# Note: File patch truncated due to size limit"
            )

        chunk = f"# File: {file.filename}\n{patch}"

        if total_size + len(chunk) > MAX_TOTAL_SIZE:
            code_chunks.append(
                "# Note: Total size limit reached. Remaining files skipped"
            )

        code_chunks.append(chunk)

        total_size += len(chunk)
    
    if not code_chunks:
        raise ValueError("No reviewable code found in this PR.")

    return "\n\n".join(code_chunks)

def get_code_from_repo(repo_url: str) -> str:
    parts = repo_url.strip("/").split("/")

    if len(parts) < 5:
        raise ValueError("Invalid repo URL format.")

    owner = parts[3]
    repo_name = parts[4]

    repo = g.get_repo(f"{owner}/{repo_name}")

    code_chunks = []

    total_size = 0

    queue = deque()

    try:
        root_contents = repo.get_contents("")

    except Exception as e:
        raise ValueError(f"Failed to fetch repository contents: {e}")

    for item in root_contents:
        queue.append((item, 0))

    while queue:

        if len(code_chunks) >= MAX_FILES:
            code_chunks.append(
                f"# Note: Review limited to first {MAX_FILES} files."
            )
            break

        item, depth = queue.popleft()

        if depth > MAX_DIRECTORY_DEPTH:
            continue

        if should_skip_path(item.path):
            continue

        if item.type == "dir":

            try:
                children = repo.get_contents(item.path)

                for child in children:
                    queue.append((child, depth + 1))

            except Exception:
                continue

            continue

        if not item.path.endswith(ALLOWED_EXTENSIONS):
            continue

        try:
            decoded = item.decoded_content.decode()

        except Exception:
            continue

        if len(decoded) > MAX_FILE_SIZE:
            decoded = (
                decoded[:MAX_FILE_SIZE]
                + "\n# Note: File truncated due to size limit."
            )

        chunk = f"# File: {item.path}\n{decoded}"

        if total_size + len(chunk) > MAX_TOTAL_SIZE:
            code_chunks.append(
                "# Note: Total size limit reached. Remaining files skipped."
            )
            break

        code_chunks.append(chunk)

        total_size += len(chunk)

    if not code_chunks:
        raise ValueError("No reviewable code files found in this repo.")

    return "\n\n".join(code_chunks)


def get_code_from_github(url: str) -> str:
    if "/pull/" in url:
        return get_code_from_pr(url)
    else:
        return get_code_from_repo(url)