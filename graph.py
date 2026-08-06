from langgraph.graph import StateGraph, START, END

from state import ReviewState

from agent import (
    bug_agent,
    security_agent,
    performance_agent,
    final_agent
)


def create_graph():

    graph = StateGraph(ReviewState)

    graph.add_node("bug_agent", bug_agent)
    graph.add_node("security_agent", security_agent)
    graph.add_node("performance_agent", performance_agent)
    graph.add_node("final_agent", final_agent)

    graph.add_edge(START, "bug_agent")
    graph.add_edge("bug_agent", "security_agent")
    graph.add_edge("security_agent", "performance_agent")
    graph.add_edge("performance_agent", "final_agent")
    graph.add_edge("final_agent", END)

    return graph.compile()