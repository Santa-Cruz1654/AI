from datetime import datetime

from app.models import (
    DocumentResult,
    ProcessingStatus,
)


class ResultStore:

    def __init__(self):

        self.results: dict[
            str,
            DocumentResult
        ] = {}


    def create(
        self,
        document_id: str,
    ) -> DocumentResult:

        record = DocumentResult(
            document_id=document_id,
            status=ProcessingStatus.PENDING,
            created_at=datetime.utcnow(),
        )

        self.results[document_id] = record

        return record


    def get(
        self,
        document_id: str,
    ) -> DocumentResult | None:

        return self.results.get(document_id)


    def set_status(
        self,
        document_id: str,
        status: ProcessingStatus,
    ) -> None:

        record = self.results[document_id]

        record.status = status

        now = datetime.utcnow()

        if status == ProcessingStatus.PROCESSING:

            record.started_at = now

        elif status in (
            ProcessingStatus.SUCCESS,
            ProcessingStatus.FAILED,
        ):

            record.completed_at = now


    def set_result(
        self,
        document_id: str,
        result: str,
    ) -> None:

        self.results[document_id].result = result


    def set_error(
        self,
        document_id: str,
        error: str,
    ) -> None:

        self.results[document_id].error = error


    def set_attempts(
        self,
        document_id: str,
        attempts: int,
    ) -> None:

        self.results[document_id].attempts = attempts