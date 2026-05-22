from state import ReviewState
from langgraph.graph import StateGraph, END
import asyncio
from agents import bug_agent, security_agent, style_agent, performance_agent, synthesizer_agent, autofix_agent

async def run_parallel_agents(state: ReviewState) -> ReviewState:
    print("Running specialized agents in parallel...\n")
    bugs, security, style, performance = await asyncio.gather(
        bug_agent(state["code"]),
        security_agent(state["code"]),
        style_agent(state["code"]),
        performance_agent(state["code"])
    )
    return {
        "bug_result": bugs,
        "security_result": security,
        "style_result": style,
        "performance_result": performance
    }

async def run_synthesizer(state: ReviewState) -> ReviewState:
    print("Synthesizing results... \n")
    report = await synthesizer_agent(
        state["bug_result"],
        state["security_result"],
        state["style_result"],
        state["performance_result"]
    )
    return {
        "final_report": report
    }

async def run_autofix(state: ReviewState) -> ReviewState:
    print("Running autofix agent... \n")
    fixed = await autofix_agent(state["code"], state["final_report"])
    return {"fixed_code": fixed}

def build_graph():
    graph = StateGraph(ReviewState)

    graph.add_node("parallel_agents", run_parallel_agents)
    graph.add_node("synthesizer", run_synthesizer)
    graph.add_node("autofix", run_autofix)

    graph.set_entry_point("parallel_agents")
    graph.add_edge("parallel_agents", "synthesizer")
    graph.add_edge("synthesizer", "autofix")
    graph.add_edge("autofix", END)
    
    return graph.compile()