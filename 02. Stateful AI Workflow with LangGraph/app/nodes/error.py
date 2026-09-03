from app.state import State
from app.utils.tracing import print_state, print_update


def handle_error(state: State) -> dict:
    """
    Handle workflow errors.
    """

    print_state(
        "STATE ENTERING: ERROR HANDLER",
        state
    )

    error_message = state.get(
        "error",
        "Unknown workflow error."
    )

    response = (
        "The workflow could not complete successfully.\n\n"
        f"Error: {error_message}"
    )

    update = {
        "final_response": response
    }

    print_update(
        "error handler",
        update
    )

    return update