# Autonomous Code Review Agent

An autonomous multi-agent system that reviews code for bugs, security vulnerabilities, style issues, and performance problems, along with providing solutions and code fixes for users to learn and implement, powered by OpenAI GPT-4o and LangGraph.

## Live Demo
[autonomous-code-review-agent.vercel.app](https://autonomous-code-review-agent.vercel.app)

## How It Works

Code is passed through 4 specialized AI agents — bug, security, style, and performance — that run in parallel, each focused on a specific domain. A suggester agent then generates actionable fix suggestions based on all findings, followed by an auto-fix agent that rewrites the code with all fixes applied. Results are returned in dedicated sections for each concern.

```mermaid
graph TD
    A[Code Input\nPaste Code or GitHub URL] --> B[GitHub Integration\nFetch code from repo or PR]
    B --> C[LangGraph Orchestrator]
    A --> C

    C --> D[Bug Detector Agent]
    C --> E[Security Scanner Agent]
    C --> F[Style Checker Agent]
    C --> G[Performance Agent]

    D --> H[Suggester Agent \nActionable fix suggestions]
    E --> H
    F --> H
    G --> H

    H --> I[Auto-Fix Agent\nRewrites code with fixes]

    I --> J[Sectioned Report + Fixed Code]

    style A fill:#1a1a1a,color:#ffffff,stroke:#555
    style C fill:#1a1a1a,color:#ffffff,stroke:#555
    style H fill:#1a1a1a,color:#ffffff,stroke:#555
    style I fill:#1a1a1a,color:#ffffff,stroke:#555
    style J fill:#2d5a27,color:#ffffff,stroke:#555
    style D fill:#1a3a5c,color:#ffffff,stroke:#555
    style E fill:#1a3a5c,color:#ffffff,stroke:#555
    style F fill:#1a3a5c,color:#ffffff,stroke:#555
    style G fill:#1a3a5c,color:#ffffff,stroke:#555
    style B fill:#3a2a1a,color:#ffffff,stroke:#555
```

## Tech Stack

| Tool | Purpose |
|---|---|
| **OpenAI GPT-4o** | Powers each specialized agent |
| **LangGraph** | Multi-agent orchestration and state management |
| **AsyncIO** | Runs all agents in parallel for faster results |
| **GitHub API** | Fetches code from repos and PRs automatically |
| **FastAPI** | REST API backend |
| **Docker** | Containerized for easy local setup |
| **Railway** | Backend deployment |
| **Vercel** | Frontend deployment |
| **DeepEval** | Agent output evaluation and accuracy testing |

## Features

- **Multi-agent parallel execution** — 4 specialized agents run simultaneously, not sequentially
- **GitHub integration** — point it at any public repo or PR link and it fetches the code automatically
- **Auto-fix mode** — returns corrected code alongside the review report
- **REST API** — fully exposed via FastAPI, accessible from any client
- **Rate limiting** — prevents API abuse and controls OpenAI token costs
- **CORS enabled** — frontend and backend communicate across different domains
- **Concurrent request limiting** — prevents multiple simultaneous requests per IP
- **Agent evaluation** — DeepEval test suite with 84%+ pass rate across 13 test cases
- **Smart GitHub traversal** — BFS traversal with file size limits, skip directories, and extension filtering
- **Per-file lazy review** — GitHub repos and PRs show a file list first, agents only run when a specific file is selected, with results cached per file
- **Sectioned review output** — results split into dedicated sections for bugs, security, style, performance, suggested fixes, and fixed code

## Getting Started

### Prerequisites
- Docker installed — [docker.com](https://docker.com)
- OpenAI API key — [platform.openai.com](https://platform.openai.com)
- GitHub Personal Access Token — [github.com/settings/tokens](https://github.com/settings/tokens)
- DeepEval (for running evaluation tests) — `pip install deepeval`

### Option 1 — Docker (Recommended)

```bash
git clone https://github.com/B0nitoFlakes/autonomous-code-review-agent.git
cd autonomous-code-review-agent
```

Create a `.env` file in the root:

```
OPENAI_API_KEY=your-openai-api-key
GITHUB_TOKEN=your-github-token
```

Then run:

```bash
docker-compose up --build
```

- Backend: `http://localhost:8000`
- Frontend: `http://localhost:3000`
- API Docs: `http://localhost:8000/docs`

### Option 2 — Manual Setup

```bash
git clone https://github.com/B0nitoFlakes/autonomous-code-review-agent.git
cd autonomous-code-review-agent

python -m venv venv
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate     # Windows

pip install -r requirements.txt
```

Create a `.env` file in the root:

```
OPENAI_API_KEY=your-openai-api-key
GITHUB_TOKEN=your-github-token
```

Run the backend:

```bash
cd backend
uvicorn main:app --reload
```

Open `frontend/index.html` with Live Server or any browser.

## API Endpoints

For API testing purposes, full interactive API documentation available at your deployed backend URL or in your own `http://localhost:8000/docs`.

### Review Code
```
POST /review/code
```
```json
{
    "code": "your code here"
}
```

### Review GitHub URL
```
POST /review/github
```
```json
{
    "url": "https://github.com/username/repo"
}
```

### Review File (GitHub lazy loading)
```
POST /review/file
```
```json
{
    "filename": "src/agents.py",
    "code": "your file code here"
}
```

### Health Check
```
GET /
```

## Sample Output

**Review Report:**
```
BUGS FOUND
1. SQL Injection Risk (Line 2): Direct string concatenation vulnerable to injection
2. Hardcoded Password (Line 3): Credentials should not be stored in source code
3. Unused nested loop (Lines 5-7): result list is never populated

SECURITY ISSUES
1. SQL query is not parameterized, vulnerable to injection attacks
2. Password hardcoded in plain text

CODE STYLE
1. Missing docstring on get_user function
2. Parameter named id shadows Python built-in

PERFORMANCE
1. Unnecessary nested loop on Lines 5-7, O(n²) complexity

SUGGESTED FIXES
1. Use parameterized queries instead of string concatenation
2. Move credentials to environment variables
3. Remove redundant nested loop
```

**Fixed Code:**
```python
def get_user(user_id):
    """Retrieve user from database by ID."""
    query = "SELECT * FROM users WHERE id = ?"
    cursor.execute(query, (user_id,))
    return cursor.fetchall()
```

## Running Evaluation Tests

Evaluation tests are run locally using DeepEval to measure the accuracy of the agent's code review output. Tests are not part of the deployment and are intended to be run during development when agent prompts or models are updated.

```bash
cd autonomous-code-review-agent
python tests/eval.py
```

Runs 13 test cases across 5 categories — vulnerable code, clean code, edge cases, partially vulnerable, and misleading code. Uses DeepEval GEval metric to score agent accuracy.

## Roadmap

- [x] Multi-agent system with parallel execution
- [x] LangGraph orchestration
- [x] GitHub PR and repo integration
- [x] Auto-fix mode
- [x] FastAPI REST endpoint
- [x] Rate limiting
- [x] Docker setup
- [x] Deployed on Railway + Vercel
- [x] DeepEval evaluation test suite
- [x] GitHub integration with BFS traversal and size limits
- [x] Concurrent request limiting
- [x] Per-file lazy review with frontend caching
- [x] Sectioned review output per concern
- [x] Suggester agent replacing synthesizer for actionable fixes
- [ ] Environment variable validation on startup
- [ ] Retry logic on OpenAI API calls for rate limits and transient failures
- [ ] Redis for distributed caching and active request tracking
- [ ] Cache TTL — auto-expire cached file results
- [ ] Async GitHub client to avoid blocking the event loop
- [ ] External linter or test runner to objectively verify auto-fixed code
- [ ] React + TypeScript frontend rebuild
- [ ] Support for local models via Ollama for privacy-sensitive codebases

## Known Limitations

- LLM may occasionally produce inconsistent reviews across runs
- Rate limited to 2 requests per minute per IP for code review, 5 requests per minute for GitHub URL submission
- Code is sent to OpenAI API — not recommended for proprietary or sensitive codebases
- Sync GitHub client may cause minor event loop blocking on large repo traversals

## Author

**Marco Setiawan** — [github.com/B0nitoFlakes](https://github.com/B0nitoFlakes)

## License

[MIT LICENSE](LICENSE)