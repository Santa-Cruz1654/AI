from langchain_groq import ChatGroq

from app.config import Settings


def create_llm(
    settings: Settings,
) -> ChatGroq:

    return ChatGroq(
        model=settings.model_name,
        temperature=settings.temperature,
        max_retries=0,
        api_key=settings.groq_api_key,
    )
