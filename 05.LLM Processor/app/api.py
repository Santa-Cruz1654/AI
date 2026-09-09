import os

from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.batch import process_batch
from app.config import Settings
from app.llm import create_llm
from app.models import Document
from app.streaming import stream_document
from app.tracking import ResultStore


# ---------------------------------------------------------
# FastAPI application
# ---------------------------------------------------------

app = FastAPI(
    title="LLM Processor",
    description=(
        "Production-style LLM processing service "
        "with streaming and batch execution."
    ),
    version="1.0.0",
)


# ---------------------------------------------------------
# Request models
# ---------------------------------------------------------

class DocumentInput(BaseModel):
    document_id: str
    text: str


class BatchRequest(BaseModel):
    documents: list[DocumentInput]


class StreamRequest(BaseModel):
    document: str


# ---------------------------------------------------------
# Application configuration
# ---------------------------------------------------------

groq_api_key = os.getenv("GROQ_API_KEY")

if not groq_api_key:
    raise RuntimeError(
        "GROQ_API_KEY environment variable is not set."
    )

settings = Settings(
    groq_api_key=groq_api_key
)

llm = create_llm(settings)

store = ResultStore()


# ---------------------------------------------------------
# Basic endpoints
# ---------------------------------------------------------

@app.get("/")
async def root():
    return {
        "service": "LLM Processor",
        "status": "running",
    }


@app.get("/health")
async def health():
    return {
        "status": "healthy",
    }


# ---------------------------------------------------------
# Batch endpoint
# ---------------------------------------------------------

@app.post("/batch")
async def batch(request: BatchRequest):

    documents = [
        Document(
            document_id=document.document_id,
            text=document.text,
        )
        for document in request.documents
    ]

    await process_batch(
        documents=documents,
        llm=llm,
        settings=settings,
        store=store,
    )

    return {
        "documents": [
            store.get(document.document_id)
            for document in documents
        ]
    }


# ---------------------------------------------------------
# Streaming endpoint
# ---------------------------------------------------------

@app.post("/stream")
async def stream(request: StreamRequest):

    return StreamingResponse(
        stream_document(
            llm=llm,
            document=request.document,
        ),
        media_type="text/plain",
    )