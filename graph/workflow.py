from langgraph.graph import StateGraph, END

from graph.state import RAGState
from graph.nodes import (
    retrieve,
    generate,
    evaluate,
    reformulate
)


def check_critic(state):

    critique = state["critique"].upper()

    # Critic approved the answer
    if "VERDICT: PASS" in critique:
        print("\n✅ CRITIC PASSED")
        return "pass"

    # Critic rejected the answer
    print("\n❌ CRITIC FAILED")

    # Stop if maximum healing attempts reached
    if state["attempts"] >= 2:
        print("\n🛑 MAXIMUM HEALING ATTEMPTS REACHED")
        return "failed"

    return "heal"


def build_graph():

    workflow = StateGraph(RAGState)

    workflow.add_node("retrieve", retrieve)
    workflow.add_node("generate", generate)
    workflow.add_node("critic", evaluate)
    workflow.add_node("reformulate", reformulate)

    workflow.set_entry_point("retrieve")

    workflow.add_edge("retrieve", "generate")
    workflow.add_edge("generate", "critic")

    workflow.add_conditional_edges(
        "critic",
        check_critic,
        {
            "pass": END,
            "heal": "reformulate",
            "failed": END
        }
    )

    workflow.add_edge("reformulate", "retrieve")

    return workflow.compile()