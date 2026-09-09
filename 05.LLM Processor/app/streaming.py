from collections.abc import AsyncIterator

from langchain.messages import (
    SystemMessage,
    HumanMessage,
)

from langchain_groq import ChatGroq


SYSTEM_PROMPT = (
    "You are a document analysis assistant. "
    "Analyze the user's document accurately and "
    "provide a concise response."
)


async def stream_document(
    llm: ChatGroq,
    document: str,
) -> AsyncIterator[str]:

    messages = [
        SystemMessage(
            content=SYSTEM_PROMPT
        ),
        HumanMessage(
            content=document
        ),
    ]

    async for chunk in llm.astream(messages):

        if chunk.content:

            yield chunk.content