import asyncio
from graph import build_graph
from github_integration import get_code_from_github

async def review_code(code: str) -> str:
    graph = build_graph()
    result = await graph.ainvoke({"code": code})
    return result["final_report"]

async def review_github(url: str) -> str:
    print(f"Fetching code from {url}...\n")
    code = get_code_from_github(url)
    return await review_code(code)

if __name__ == "__main__":
    url = "https://github.com/B0nitoFlakes/autonomous-code-review-agent/pull/2"
    result = asyncio.run(review_github(url))
    print(result)