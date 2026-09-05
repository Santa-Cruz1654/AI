def measure_context(messages):

    total_characters = 0

    for message in messages:

        content = message.content

        if isinstance(content, str):
            total_characters += len(content)

    approximate_tokens = total_characters // 4

    return {
        "message_count": len(messages),
        "approximate_tokens": approximate_tokens,
    }