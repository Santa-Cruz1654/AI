CONTEXT_BUDGET = 8000

SYSTEM_BUDGET = 1000
SUMMARY_BUDGET = 2000
RECENT_MESSAGES_BUDGET = 3500
TOOL_CONTEXT_BUDGET = 1500


def get_context_budget() -> dict:
    """
    Return the approximate context allocation.

    Total budget:

        System instructions     = 1000
        Conversation summary    = 2000
        Recent messages         = 3500
        Tool context            = 1500
        --------------------------------
        Total                   = 8000
    """

    return {
        "total": CONTEXT_BUDGET,
        "system": SYSTEM_BUDGET,
        "summary": SUMMARY_BUDGET,
        "recent_messages": RECENT_MESSAGES_BUDGET,
        "tool_context": TOOL_CONTEXT_BUDGET,
    }


def approximate_tokens(text: str) -> int:
    """
    Very rough token estimate.

    This is intentionally simple because the goal of this
    project is to understand context engineering, not to
    build a tokenizer.

    Rule of thumb:

        approximately 4 characters ≈ 1 token
    """

    if not text:
        return 0

    return max(1, len(text) // 4)


def message_token_count(message) -> int:
    """
    Estimate the token count of one LangChain message.
    """

    content = getattr(message, "content", "")

    if not isinstance(content, str):
        content = str(content)

    return approximate_tokens(content)


def context_token_count(messages) -> int:
    """
    Estimate the total number of tokens across messages.
    """

    return sum(
        message_token_count(message)
        for message in messages
    )