from app.state import State
from app.llm import get_llm
from app.schemas import ReviewResult
from app.utils.tracing import print_state, print_update


MAX_REVISIONS = 3


def review_plan(state: State) -> dict:
    """
    Review the generated plan using Groq structured output.

    Reads:
        request
        analysis
        plan
        revision_count

    Updates:
        review
        approval
        error
    """

    print_state(
        "STATE ENTERING: REVIEW PLAN",
        state
    )

    plan = state["plan"]

    # -----------------------------------------
    # Validate plan
    # -----------------------------------------

    if not plan:
        update = {
            "review": "No plan was generated.",
            "approval": False,
            "error": "Plan generation failed."
        }

        print_update("review plan", update)

        return update

    # -----------------------------------------
    # Maximum revision protection
    # -----------------------------------------

    if state["revision_count"] >= MAX_REVISIONS:
        update = {
            "review": (
                "Maximum number of revisions reached. "
                "The workflow will stop."
            ),
            "approval": False,
            "error": "Maximum revisions exceeded."
        }

        print_update("review plan", update)

        return update

    # -----------------------------------------
    # Create structured-output LLM
    # -----------------------------------------

    llm = get_llm()

    structured_llm = llm.with_structured_output(
        ReviewResult
    )

    # -----------------------------------------
    # Reviewer prompt
    # -----------------------------------------

    prompt = f"""
You are a strict plan reviewer.

Review the plan against the original user request.

Original request:
{state["request"]}

Request analysis:
{state["analysis"]}

Plan:
{state["plan"]}

Evaluate whether the plan:

1. Directly addresses the request
2. Is clear and structured
3. Contains sufficient detail
4. Covers the important requirements
5. Is logically organized
6. Can realistically satisfy the request

If the plan is good enough, choose "approved".

If meaningful improvements are required, choose "revise".

If you choose "revise", provide specific suggestions
that the planner can use to improve the plan.
"""

    # -----------------------------------------
    # Invoke Groq
    # -----------------------------------------

    try:
        result = structured_llm.invoke(prompt)

        update = {
            "review": result.review,
            "suggestions": result.suggestions,
            "approval": result.decision == "approved",
        }

        print_update(
            "review plan",
            update
        )

        return update

    except Exception as e:

        update = {
            "review": "The plan could not be reviewed.",
            "approval": False,
            "error": str(e)
        }

        print_update(
            "review plan",
            update
        )

        return update