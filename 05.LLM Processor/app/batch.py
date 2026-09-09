import asyncio

from langchain.messages import (
    SystemMessage,
    HumanMessage,
)
from langchain_groq import ChatGroq

from app.config import Settings
from app.models import (
    Document,
    ProcessingStatus,
)
from app.retry import retry_with_backoff
from app.tracking import ResultStore


SYSTEM_PROMPT = (
    "You are a document analysis assistant. "
    "Analyze the document accurately and "
    "provide a concise summary."
)


async def process_document(
    document: Document,
    llm: ChatGroq,
    semaphore: asyncio.Semaphore,
    settings: Settings,
    store: ResultStore,
) -> None:
    """
    Process one document.

    The document moves through the following lifecycle:

        PENDING
           ↓
        PROCESSING
           ↓
        LLM operation
           ↓
        SUCCESS / FAILED

    The LLM operation is protected by:

        - concurrency control
        - retry handling
        - empty-response validation
        - result tracking
    """

    document_id = document.document_id

    # ---------------------------------------------------------
    # 1. Mark document as PROCESSING
    # ---------------------------------------------------------

    store.set_status(
        document_id,
        ProcessingStatus.PROCESSING,
    )

    # ---------------------------------------------------------
    # 2. Define the actual LLM operation
    # ---------------------------------------------------------

    async def operation():
        """
        Execute the LLM call for this document.

        The semaphore ensures that no more than
        settings.max_concurrency LLM calls are active
        at the same time.
        """

        async with semaphore:

            messages = [
                SystemMessage(
                    content=SYSTEM_PROMPT
                ),
                HumanMessage(
                    content=document.text
                ),
            ]

            response = await llm.ainvoke(
                messages
            )

            return response.content

    # ---------------------------------------------------------
    # 3. Execute with retry handling
    # ---------------------------------------------------------

    try:

        result, attempts = await retry_with_backoff(
            operation=operation,
            max_attempts=settings.max_attempts,
            base_delay=settings.base_retry_delay,
        )

        # -----------------------------------------------------
        # 4. Validate the LLM result
        # -----------------------------------------------------
        #
        # A successful API request does not necessarily mean
        # that our application received a usable result.
        #
        # If the LLM returns an empty response, treat that as
        # a failed document-processing operation.
        # -----------------------------------------------------

        if not result or not result.strip():

            raise ValueError(
                "LLM returned an empty response"
            )

        # -----------------------------------------------------
        # 5. Store actual attempt count
        # -----------------------------------------------------

        store.set_attempts(
            document_id,
            attempts,
        )

        # -----------------------------------------------------
        # 6. Store successful result
        # -----------------------------------------------------

        store.set_result(
            document_id,
            result,
        )

        # -----------------------------------------------------
        # 7. Mark document as SUCCESS
        # -----------------------------------------------------

        store.set_status(
            document_id,
            ProcessingStatus.SUCCESS,
        )

    # ---------------------------------------------------------
    # 8. Handle final failure
    # ---------------------------------------------------------

    except Exception as exc:

        # Store the error message.
        store.set_error(
            document_id,
            str(exc),
        )

        # Mark only this document as FAILED.
        #
        # A failure in one document does not automatically
        # fail the other documents in the batch.
        store.set_status(
            document_id,
            ProcessingStatus.FAILED,
        )


async def process_batch(
    documents: list[Document],
    llm: ChatGroq,
    settings: Settings,
    store: ResultStore,
) -> None:
    """
    Process multiple documents concurrently.

    Example:

        documents
            ↓
        process_batch()
            ↓
        create PENDING records
            ↓
        create async tasks
            ↓
        asyncio.gather()
            ↓
        process_document() for each document
            ↓
        shared Semaphore
            ↓
        bounded concurrent LLM calls
    """

    # ---------------------------------------------------------
    # 1. Create ONE shared semaphore
    # ---------------------------------------------------------
    #
    # If max_concurrency = 3, at most three LLM operations
    # can execute at the same time across the entire batch.
    # ---------------------------------------------------------

    semaphore = asyncio.Semaphore(
        settings.max_concurrency
    )

    # ---------------------------------------------------------
    # 2. Create tracking records
    # ---------------------------------------------------------
    #
    # Every document starts in PENDING state.
    # ---------------------------------------------------------

    for document in documents:

        store.create(
            document.document_id
        )

    # ---------------------------------------------------------
    # 3. Create one coroutine for every document
    # ---------------------------------------------------------

    tasks = [
        process_document(
            document=document,
            llm=llm,
            semaphore=semaphore,
            settings=settings,
            store=store,
        )
        for document in documents
    ]

    # ---------------------------------------------------------
    # 4. Execute all document operations concurrently
    # ---------------------------------------------------------
    #
    # asyncio.gather() allows all tasks to make progress
    # concurrently.
    #
    # The shared semaphore prevents unlimited concurrent
    # LLM requests.
    # ---------------------------------------------------------

    await asyncio.gather(
        *tasks
    )