import os

from dataclasses import dataclass

from dotenv import load_dotenv


load_dotenv()


@dataclass(frozen=True)
class Settings:

    groq_api_key: str
    model_name: str = "openai/gpt-oss-120b"

    temperature: float = 0.0

    max_concurrency: int = 3

    max_attempts: int = 3

    base_retry_delay: float = 1.0


def load_settings() -> Settings:

    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        raise RuntimeError(
            "GROQ_API_KEY is not set"
        )

    return Settings(
        groq_api_key=api_key,
    )