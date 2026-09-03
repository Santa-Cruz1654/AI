from langgraph.graph import StateGraph, START, END

from app.state import State

from app.nodes.analyze import analyze_request
from app.nodes.planner import generate_plan
from app.nodes.reviewer import review_plan
from app.nodes.response import final_response
from app.nodes.error import handle_error

from app.routing.review_router import route_after_review


def build_graph():
    """
    Build and compile the LangGraph workflow.
    """

    workflow = StateGraph(State)

    # -----------------------------------------
    # Add nodes
    # -----------------------------------------

    workflow.add_node(
        "analyze_request",
        analyze_request
    )

    workflow.add_node(
        "generate_plan",
        generate_plan
    )

    workflow.add_node(
        "review_plan",
        review_plan
    )

    workflow.add_node(
        "final_response",
        final_response
    )

    workflow.add_node(
        "handle_error",
        handle_error
    )

    # -----------------------------------------
    # Normal edges
    # -----------------------------------------

    workflow.add_edge(
        START,
        "analyze_request"
    )

    workflow.add_edge(
        "analyze_request",
        "generate_plan"
    )

    workflow.add_edge(
        "generate_plan",
        "review_plan"
    )

    # -----------------------------------------
    # Conditional edge
    # -----------------------------------------

    workflow.add_conditional_edges(
        "review_plan",
        route_after_review,
        {
            "final_response": "final_response",
            "generate_plan": "generate_plan",
            "handle_error": "handle_error",
        }
    )

    # -----------------------------------------
    # End edges
    # -----------------------------------------

    workflow.add_edge(
        "final_response",
        END
    )

    workflow.add_edge(
        "handle_error",
        END
    )

    return workflow.compile()