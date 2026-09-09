from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class ProcessingStatus(str, Enum):

    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"


@dataclass
class Document:

    document_id: str
    text: str


@dataclass
class DocumentResult:

    document_id: str
    status: ProcessingStatus

    result: str | None = None
    error: str | None = None

    attempts: int = 0

    created_at: datetime | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None