from app.state import State
from app.llm import get_llm
from app.utils.tracing import print_state, print_update


def final_response(state: State) -> dict:
    """
    Generate the final answer using the approved plan.

    Reads:
        state["request"]
        state["analysis"]
        state["plan"]
        state["review"]
        state["approval"]
        state["revision_count"]

    Updates:
        state["final_response"]
        state["error"]
    """

    print_state(
        "STATE ENTERING: FINAL RESPONSE",
        state
    )

    # --------------------------------------------------
    # Validate approval
    # --------------------------------------------------

    if not state["approval"]:
        update = {
            "final_response": "",
            "error": "Cannot generate final response because the plan was not approved."
        }

        print_update("final response", update)

        return update

    # --------------------------------------------------
    # Generate final answer
    # --------------------------------------------------

    try:
        llm = get_llm()

        prompt = f"""
You are a helpful AI assistant.

Generate the final answer to the user's request using the
analysis, approved plan, and review provided below.

Original user request:
{state["request"]}

Request analysis:
{state["analysis"]}

Approved plan:
{state["plan"]}

Review:
{state["review"]}

Revision count:
{state["revision_count"]}

Follow the approved plan and directly answer the user's
original request.

Do not talk about the internal workflow, state, nodes,
review process, or LangGraph implementation unless the
user explicitly asked about them.

Return only the final answer.
"""

        response = llm.invoke(prompt)

        update = {
            "final_response": response.content,
            "error": ""
        }

        print_update(
            "final response",
            update
        )

        return update

    except Exception as e:

        update = {
            "final_response": "",
            "error": str(e)
        }

        print_update(
            "final response",
            update
        )

        return update