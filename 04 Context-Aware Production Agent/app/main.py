from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver

from app.models.model import model

from app.context.middleware import (
    runtime_context_prompt,
    context_budget_middleware,
)

from app.context.summarizer import (
    summarization_middleware,
)

from app.context.metrics import (
    measure_context,
)


# ============================================================
# CHECKPOINTER
# ============================================================

checkpointer = InMemorySaver()


# ============================================================
# AGENT
# ============================================================

agent = create_agent(
    model=model,
    tools=[],

    middleware=[
        runtime_context_prompt,
        summarization_middleware,
        context_budget_middleware,
    ],

    checkpointer=checkpointer,

    context_schema=dict,

    system_prompt=(
        "You are a helpful customer support assistant. "
        "Answer customer questions clearly and accurately."
    ),
)


# ============================================================
# CHAT
# ============================================================

def chat(
    thread_id: str,
    message: str,
):
    """
    Send one user message to the agent.

    thread_id:
        Identifies the conversation.

    message:
        New user message.

    Runtime context:
        Information about the current execution/user.
        This is NOT stored as conversation history.
    """

    # --------------------------------------------------------
    # Runtime context
    # --------------------------------------------------------

    runtime_context = {
        "user_id": "customer-001",

        "account_type": "premium",

        "permissions": [
            "order_read",
            "order_update",
        ],

        "environment": "production",

        "region": "US",
    }

    # --------------------------------------------------------
    # Conversation configuration
    # --------------------------------------------------------

    config = {
        "configurable": {
            "thread_id": thread_id,
        }
    }

    # --------------------------------------------------------
    # Invoke agent
    # --------------------------------------------------------

    result = agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": message,
                }
            ]
        },

        config=config,

        context=runtime_context,
    )

    # --------------------------------------------------------
    # Persisted state
    # --------------------------------------------------------

    messages = result["messages"]

    metrics = measure_context(messages)

    print(
        "[State] "
        f"messages={metrics['message_count']} "
        f"approx_tokens={metrics['approximate_tokens']}"
    )

    # --------------------------------------------------------
    # Return agent result
    # --------------------------------------------------------

    return result


# ============================================================
# CLI
# ============================================================

if __name__ == "__main__":

    thread_id = "customer-001"

    print(
        "Context-Aware Customer Support Agent"
    )

    print(
        "Type 'exit' to stop.\n"
    )

    while True:

        user_input = input("You: ")

        if user_input.lower() == "exit":
            break

        result = chat(
            thread_id=thread_id,
            message=user_input,
        )

        response = result["messages"][-1]

        print(
            f"Assistant: {response.content}\n"
        )