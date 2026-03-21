from langgraph.graph import StateGraph, END
from app.graph.state import GraphState
from app.graph.node.fetch_pr import fetch_pr_node
from app.graph.node.agent_quality import agent_quality_node
from app.graph.node.agent_security import agent_security_node
from app.graph.node.agent_performance import agent_performance_node
from app.graph.node.agent_reviewer import agent_reviewer_node


def build_review_graph():
    """
    Graph flow:
    fetch_pr → [quality, security, performance in PARALLEL] → reviewer → END
    """
    graph = StateGraph(GraphState)

    # Register all nodes
    graph.add_node("fetch_pr", fetch_pr_node)
    graph.add_node("agent_quality", agent_quality_node)
    graph.add_node("agent_security", agent_security_node)
    graph.add_node("agent_performance", agent_performance_node)
    graph.add_node("agent_reviewer", agent_reviewer_node)

    # Entry point
    graph.set_entry_point("fetch_pr")

    # fetch_pr fans out to all 3 agents IN PARALLEL
    graph.add_edge("fetch_pr", "agent_quality")
    graph.add_edge("fetch_pr", "agent_security")
    graph.add_edge("fetch_pr", "agent_performance")

    # All 3 agents fan in to reviewer
    graph.add_edge("agent_quality", "agent_reviewer")
    graph.add_edge("agent_security", "agent_reviewer")
    graph.add_edge("agent_performance", "agent_reviewer")

    # Reviewer ends the graph
    graph.add_edge("agent_reviewer", END)

    return graph.compile()


# Singleton — compiled once at startup
review_graph = build_review_graph()