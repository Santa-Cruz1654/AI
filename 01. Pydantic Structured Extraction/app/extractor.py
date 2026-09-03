from dotenv import load_dotenv
from groq import BadRequestError
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

from app.schemas import Person


load_dotenv()


class ExtractionError(Exception):
    """Raised when structured extraction fails."""


model = ChatGroq(
    model="openai/gpt-oss-20b",
    temperature=0,
)


prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
            Extract information from the user's text into the provided
            Person schema.

            Follow these rules strictly:

            - Extract only information explicitly supported by the text.
            - Do not infer or guess missing information.
            - The age field must represent the person's current age.
            - Do not use historical ages, such as the person's age when
              they joined a company.
            - If the current age is not explicitly stated, return null.
            - Only extract experience_years when the number of years of
              professional experience is explicitly stated.
            - If a field cannot be determined reliably, return null.
            """,
        ),
        (
            "human",
            "{text}",
        ),
    ]
)


structured_model = (
    prompt
    | model.with_structured_output(Person)
).with_retry(
    stop_after_attempt=3,
)


def extract_person(text: str) -> Person:
    try:
        return structured_model.invoke({"text": text})

    except BadRequestError as e:
        raise ExtractionError(
            "The LLM could not produce valid structured output."
        ) from e