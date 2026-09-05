from langchain.agents.middleware import SummarizationMiddleware

from app.models.model import model


summarization_middleware = SummarizationMiddleware(
    model=model,
    trigger=("tokens", 4000),
    keep=("messages", 6),
)