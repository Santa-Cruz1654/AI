from app.state import State
from app.llm import get_llm
from app.utils.tracing import print_state, print_update


def generate_plan(state: State) -> dict:
    """
    Generate or revise a plan using Groq.

    Reads:
        request
        analysis
        plan
        review
        suggestions
        revision_count

    Updates:
        plan
        revision_count
    """

    print_state(
        "STATE ENTERING: GENERATE PLAN",
        state
    )

    llm = get_llm()

    revision_count = state["revision_count"]

    prompt = f"""
You are a planning assistant.

Original user request:
{state["request"]}

Analysis of the request:
{state["analysis"]}

Previous plan:
{state["plan"]}

Previous review:
{state["review"]}

Specific improvement suggestions:
{state["suggestions"]}

Generate a clear and structured plan that satisfies
the original user request.

If this is a revision, improve the previous plan using
the review and specific suggestions.

Do not blindly copy the previous plan.

Make meaningful improvements where required.

Return only the numbered plan.
"""

    try:
        response = llm.invoke(prompt)

        update = {
            "plan": response.content,
            "revision_count": revision_count + 1,
        }

        print_update(
            "generate plan",
            update
        )

        return update

    except Exception as e:

        update = {
            "error": str(e)
        }

        print_update(
            "generate plan",
            update
        )

        return update