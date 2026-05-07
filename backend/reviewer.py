import asyncio
from graph import build_graph
from github_integration import get_code_from_github

async def review_code(code: str) -> str:
    graph = build_graph()
    result = await graph.ainvoke({"code": code})
    return {
        "report": result["final_report"],
        "fixed_code": result["fixed_code"]
    }

async def review_github(url: str) -> str:
    print(f"Fetching code from {url}...\n")
    code = get_code_from_github(url)
    return await review_code(code)

if __name__ == "__main__":
    url = """def calculate_discount(price, discount):\n    result = price / discount\n    return result\n\nuser = {\"name\": \"Ali\"}\nprint(user[\"age\"])\n\nitems = [1, 2, 3]\nprint(items[10])"""
    result = asyncio.run(review_code(url))
    print(result)