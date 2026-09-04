"""
SATYA Ingestion Engine
Handles raw file/payload ingestion, SHA-256 content hashing, duplicate detection (idempotency),
and raw source document archiving.
"""

import hashlib
import uuid
from datetime import datetime, timezone
from typing import Tuple, Dict, Any, Optional
from backend.models.domain_models import SourceDocument, SourceType, PipelineState

class SourceIngestionService:
    def __init__(self, existing_hashes: Optional[Dict[str, SourceDocument]] = None):
        # Local hash cache for duplicate ingestion detection (idempotency)
        self.seen_hashes: Dict[str, SourceDocument] = existing_hashes if existing_hashes else {}

    def compute_sha256(self, content: str) -> str:
        return hashlib.sha256(content.encode('utf-8')).hexdigest()

    def ingest_raw_source(
        self,
        raw_content: str,
        file_name: str,
        project_id: str,
        source_type: str = SourceType.UNKNOWN,
        author: str = "Unknown",
        reporting_period: Optional[str] = None,
        submitted_at: Optional[str] = None
    ) -> Tuple[SourceDocument, bool]:
        """
        Ingests raw source text, calculates SHA-256 hash, checks for exact duplicate ingestion,
        and returns (SourceDocument, is_duplicate).
        """
        if not raw_content or not raw_content.strip():
            raise ValueError("Raw content cannot be empty.")

        content_hash = self.compute_sha256(raw_content)
        now_str = datetime.now(timezone.utc).isoformat()

        # Idempotency Check: Exact duplicate content
        if content_hash in self.seen_hashes:
            existing_doc = self.seen_hashes[content_hash]
            return existing_doc, True

        # Generate unique source ID
        source_id = f"SRC-{uuid.uuid4().hex[:8].upper()}"
        sub_time = submitted_at if submitted_at else now_str

        doc = SourceDocument(
            source_id=source_id,
            project_id=project_id,
            source_type=source_type,
            file_name=file_name,
            sha256_hash=content_hash,
            raw_content=raw_content,
            submitted_at=sub_time,
            received_at=now_str,
            author=author,
            reporting_period=reporting_period,
            extraction_status=PipelineState.INGESTED
        )

        self.seen_hashes[content_hash] = doc
        return doc, False
