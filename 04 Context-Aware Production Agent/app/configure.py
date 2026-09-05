import os

from dotenv import load_dotenv


load_dotenv()


GROQ_API_KEY = os.getenv("GROQ_API_KEY")

MODEL_NAME = os.getenv(
    "MODEL_NAME",
    "openai/gpt-oss-120b",
)
RECENT_MESSAGE_COUNT = int(
    os.getenv("RECENT_MESSAGE_COUNT", "8")
)