import asyncio
from graph import build_graph
from github_integration import get_code_from_github

async def review_code(code: str) -> str:
    graph = build_graph()
    result = await graph.ainvoke({"code": code})
    return {
        "bug_result": result["bug_result"],
        "security_result": result["security_result"],
        "style_result": result["style_result"],
        "performance_result": result["performance_result"],
        "suggested_fixes": result["suggested_fixes"],
        "fixed_code": result["fixed_code"]
    }

async def review_github(url: str) -> str:
    print(f"Fetching code from {url}...\n")
    code = get_code_from_github(url)
    return code
    # return await review_code(code)

async def review_file(filename:str, code:str) ->str:
    graph = build_graph()
    result = await graph.ainvoke({"code":code})
    return {
        "filename": filename,
        "bug_result": result["bug_result"],
        "security_result": result["security_result"],
        "style_result": result["style_result"],
        "performance_result": result["performance_result"],
        "suggested_fixes": result["suggested_fixes"],
        "fixed_code": result["fixed_code"]
    }

if __name__ == "__main__":
    url = "https://github.com/B0nitoFlakes/etl-data-pipelines"
    code_broken = """def calculate_discount(price, discount):\n    result = price / discount\n    return result\n\nuser = {\"name\": \"Ali\"}\nprint(user[\"age\"])\n\nitems = [1, 2, 3]\nprint(items[10])"""
    result = asyncio.run(review_github(url))
    print(result)