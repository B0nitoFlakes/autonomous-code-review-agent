import asyncio
from graph import build_graph
from agents import bug_agent, security_agent, style_agent, performance_agent, synthesizer_agent

async def review_code(code: str)->str:
    graph = build_graph()
    state = {"code":code}
    result = await graph.ainvoke(state)
    return result["final_report"]

# test it
if __name__ == "__main__":
    test_code = """
def get_user(id):
    query = "SELECT * FROM users WHERE id = " + id
    password = "admin123"
    result = []
    for i in range(len(result)):
        for j in range(len(result)):
            print(result[i][j])
    return result
"""
    result = asyncio.run(review_code(test_code))
    print(result)