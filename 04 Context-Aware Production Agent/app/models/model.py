import os

from dotenv import load_dotenv
from langchain_groq import ChatGroq


load_dotenv()


model = ChatGroq(
    model="openai/gpt-oss-120b",
    temperature=0.2,
    max_tokens=2048,
    api_key=os.getenv("GROQ_API_KEY"),
)