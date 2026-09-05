from collections.abc import Callable
from typing import Any

from langchain.agents.middleware import (
    ModelRequest,
    ModelResponse,
    dynamic_prompt,
    wrap_model_call,
)

from app.context.budget import (
    CONTEXT_BUDGET,
    SUMMARY_BUDGET,
    RECENT_MESSAGES_BUDGET,
    approximate_tokens,
    message_token_count,
)


# ============================================================
# RUNTIME CONTEXT
# ============================================================

@dynamic_prompt
def runtime_context_prompt(request: ModelRequest) -> str:
    """
    Dynamically construct the system prompt using
    runtime context.

    Runtime context is NOT conversation history.

    Examples:
        - user_id
        - account_type
        - permissions
        - environment
        - region
    """

    runtime = request.runtime

    context = {}

    if runtime is not None:
        context = runtime.context or {}

    user_id = context.get("user_id", "unknown")
    account_type = context.get("account_type", "standard")
    permissions = context.get("permissions", [])
    environment = context.get("environment", "unknown")
    region = context.get("region", "unknown")

    return f"""
You are a helpful customer support assistant.

Answer customer questions clearly and accurately.

Runtime context:
- User ID: {user_id}
- Account type: {account_type}
- Permissions: {permissions}
- Environment: {environment}
- Region: {region}

Important rules:

1. Never invent information.
2. Do not claim that you performed an action unless a real tool performed it.
3. Do not expose internal runtime information unless appropriate.
4. Use conversation context when it is relevant.
5. Prefer recent information when information conflicts.
6. Ask for missing information instead of inventing it.

Context budget:
- Total approximate budget: {CONTEXT_BUDGET} tokens.
- System instructions: approximately 1000 tokens.
- Conversation summary: approximately {SUMMARY_BUDGET} tokens.
- Recent conversation: approximately {RECENT_MESSAGES_BUDGET} tokens.
""".strip()


# ============================================================
# TOKEN HELPERS
# ============================================================

def _estimate_message_tokens(message: Any) -> int:
    """
    Estimate the number of tokens in a message.
    """

    return message_token_count(message)


# ============================================================
# SUMMARY DETECTION
# ============================================================

def _is_summary_message(message: Any) -> bool:
    """
    Determine whether a message appears to be a
    conversation summary.

    LangChain's summarization middleware inserts a
    summary message when summarization occurs.

    We identify it by its content.
    """

    content = getattr(message, "content", "")

    if not isinstance(content, str):
        return False

    lowered = content.lower()

    summary_markers = [
        "conversation summary",
        "summary of the conversation",
        "conversation so far",
    ]

    return any(
        marker in lowered
        for marker in summary_markers
    )


# ============================================================
# RECENT MESSAGE SELECTION
# ============================================================

def _select_recent_messages(
    messages,
    budget: int,
):
    """
    Select the newest messages that fit inside the
    allocated recent-message budget.

    We iterate backwards because the newest messages
    are the highest-priority conversational context.
    """

    selected = []

    current_tokens = 0

    for message in reversed(messages):

        # Summary messages are handled separately.
        if _is_summary_message(message):
            continue

        message_tokens = _estimate_message_tokens(message)

        if current_tokens + message_tokens > budget:
            break

        selected.append(message)

        current_tokens += message_tokens

    selected.reverse()

    return selected


# ============================================================
# SUMMARY SELECTION
# ============================================================

def _select_summary_message(
    messages,
    budget: int,
):
    """
    Find the latest conversation summary.

    The summary receives its own context allocation so that
    the context-budget middleware does not accidentally remove
    it while selecting recent messages.
    """

    for message in reversed(messages):

        if not _is_summary_message(message):
            continue

        message_tokens = _estimate_message_tokens(message)

        if message_tokens <= budget:
            return message

        # Summary is too large for its allocation.
        # Do not send an oversized summary.
        return None

    return None


# ============================================================
# CONTEXT BUDGET MIDDLEWARE
# ============================================================

@wrap_model_call
def context_budget_middleware(
    request: ModelRequest,
    handler: Callable[[ModelRequest], ModelResponse],
) -> ModelResponse:
    """
    Control how much conversation context is sent
    to the model.

    Important:

        persisted conversation
                ↓
        summarization middleware
                ↓
        context budget middleware
                ↓
        selected context
                ↓
        model

    The persisted state is NOT modified.

    We only modify the request going to the model.
    """

    messages = list(request.messages)

    # --------------------------------------------------------
    # 1. Find the conversation summary
    # --------------------------------------------------------

    summary_message = _select_summary_message(
        messages=messages,
        budget=SUMMARY_BUDGET,
    )

    # --------------------------------------------------------
    # 2. Select recent conversational messages
    # --------------------------------------------------------

    recent_messages = _select_recent_messages(
        messages=messages,
        budget=RECENT_MESSAGES_BUDGET,
    )

    # --------------------------------------------------------
    # 3. Build the final model context
    # --------------------------------------------------------

    selected_messages = []

    if summary_message is not None:
        selected_messages.append(summary_message)

    selected_messages.extend(recent_messages)

    # --------------------------------------------------------
    # 4. Calculate context metrics
    # --------------------------------------------------------

    context_tokens = sum(
        _estimate_message_tokens(message)
        for message in selected_messages
    )

    total_state_tokens = sum(
        _estimate_message_tokens(message)
        for message in messages
    )

    print(
        "[Context Budget] "
        f"state_messages={len(messages)} "
        f"state_tokens≈{total_state_tokens} "
        f"model_messages={len(selected_messages)} "
        f"model_tokens≈{context_tokens}"
    )

    # --------------------------------------------------------
    # 5. Send only selected context to the model
    # --------------------------------------------------------

    return handler(
        request.override(
            messages=selected_messages,
        )
    )