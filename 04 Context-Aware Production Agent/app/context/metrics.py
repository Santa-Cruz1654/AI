from app.context.budget import approximate_tokens


def measure_context(messages):
    """
    Measure the size of a collection of messages.

    This measures the supplied messages only.

    The context-budget middleware is responsible for
    reporting the actual model-facing context.
    """

    total_characters = 0

    for message in messages:

        content = getattr(
            message,
            "content",
            "",
        )

        if not isinstance(content, str):
            content = str(content)

        total_characters += len(content)

    return {
        "message_count": len(messages),
        "characters": total_characters,
        "approximate_tokens": approximate_tokens(
            "x" * total_characters
        ),
    }