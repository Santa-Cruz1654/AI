from app.state import State


def route_after_review(state: State) -> str:
    """
    Decide where the workflow should go after review.

    Returns:
        "final_response"
        "generate_plan"
        "handle_error"
    """

    if state["error"]:
        return "handle_error"

    if state["approval"]:
        return "final_response"

    return "generate_plan"