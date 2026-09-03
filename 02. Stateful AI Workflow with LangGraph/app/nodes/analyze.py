from app.state import State
from app.llm import get_llm
from app.utils.tracing import print_state, print_update


def analyze_request(state: State) -> dict:
    """
    Analyze the user's request using Groq.

    Reads:
        state["request"]

    Updates:
        state["analysis"]
    """

    print_state(
        "STATE ENTERING: ANALYZE REQUEST",
        state
    )

    llm = get_llm()

    prompt = f"""
Analyze the following user request.

User request:
{state["request"]}

Provide a concise analysis of:
1. What the user is asking for
2. The main objective
3. Important requirements
4. What the final answer should accomplish
"""

    response = llm.invoke(prompt)

    update = {
        "analysis": response.content
    }

    print_update(
        "analyze request",
        update
    )

    return update