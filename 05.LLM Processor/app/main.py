import asyncio

from app.batch import process_batch
from app.config import load_settings
from app.llm import create_llm
from app.models import Document
from app.streaming import stream_document
from app.tracking import ResultStore


async def run_streaming(
    llm,
) -> None:

    document = """
    Python is a programming language widely used
    for automation, data analysis, web development,
    and machine learning.
    """

    print("\nStreaming response:\n")

    async for chunk in stream_document(
        llm,
        document,
    ):

        print(
            chunk,
            end="",
            flush=True,
        )

    print("\n")


async def run_batch(
    llm,
    settings,
) -> None:

    documents = [
        Document(
            document_id="doc-001",
            text=(
                "Python is a high-level programming "
                "language used in many engineering domains."
            ),
        ),
        Document(
            document_id="doc-002",
            text=(
                "Kubernetes is a platform for "
                "container orchestration."
            ),
        ),
        Document(
            document_id="doc-003",
            text=(
                "Redis is an in-memory data store "
                "often used for caching."
            ),
        ),
        Document(
            document_id="doc-004",
            text=(
                "Kafka is a distributed event streaming "
                "platform."
            ),
        ),
    ]

    store = ResultStore()

    await process_batch(
        documents=documents,
        llm=llm,
        settings=settings,
        store=store,
    )

    print("\nBatch results:\n")

    for document_id, result in store.results.items():

        print("=" * 60)

        print(
            f"Document : {document_id}"
        )

        print(
            f"Status   : {result.status.value}"
        )

        print(
            f"Attempts : {result.attempts}"
        )

        if result.result:

            print(
                f"\nResult:\n{result.result}"
            )

        if result.error:

            print(
                f"\nError:\n{result.error}"
            )


async def main():

    settings = load_settings()

    llm = create_llm(
        settings
    )

    await run_streaming(
        llm
    )

    await run_batch(
        llm,
        settings,
    )


if __name__ == "__main__":

    asyncio.run(main())