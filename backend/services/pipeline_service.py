"""
SATYA Execution Event Pipeline Orchestrator
Coordinates: Ingest -> Normalize -> Extract -> Validate -> Persist.
Maintains correlation IDs (source_id, event_id, pipeline_run_id) and structured logging.
"""

import time
import uuid
import logging
from typing import Optional, Set, Dict, Any, List
from backend.models.domain_models import (
    SourceDocument, PipelineRunResult, PipelineState, SourceType
)
from backend.ingestion.source_ingestion import SourceIngestionService
from backend.normalization.content_normalization import ContentNormalizationService
from backend.extraction.event_extractor import ExecutionEventExtractionService
from backend.validation.event_validator import EventValidationService
from backend.persistence.database_engine import DatabaseEngine

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] [%(name)s] %(message)s")
logger = logging.getLogger("SATYA.Pipeline")

class ExecutionEventPipelineService:
    def __init__(self, db_engine: Optional[DatabaseEngine] = None, valid_vocab: Optional[Set[str]] = None):
        self.db = db_engine if db_engine else DatabaseEngine(":memory:")
        self.ingestion_service = SourceIngestionService()
        self.normalization_service = ContentNormalizationService()
        self.extraction_service = ExecutionEventExtractionService()
        self.validation_service = EventValidationService(valid_vocab)

    def set_schedule_vocabulary(self, vocab: Set[str]):
        """Sets active schedule Activity ID vocabulary for Rule 5 guardrail validation."""
        self.validation_service.set_valid_vocabulary(vocab)

    def process_source_payload(
        self,
        raw_content: str,
        file_name: str,
        project_id: str,
        source_type: str = SourceType.UNKNOWN,
        author: str = "Unknown",
        submitted_at: Optional[str] = None
    ) -> PipelineRunResult:
        """
        Executes end-to-end pipeline for a raw source input payload.
        """
        start_time = time.time()
        pipeline_run_id = f"RUN-{uuid.uuid4().hex[:8].upper()}"

        logger.info(f"[{pipeline_run_id}] Starting ingestion for file '{file_name}' (Project: {project_id})")

        # 1. Ingestion & Idempotency Check
        doc, is_duplicate = self.ingestion_service.ingest_raw_source(
            raw_content=raw_content,
            file_name=file_name,
            project_id=project_id,
            source_type=source_type,
            author=author,
            submitted_at=submitted_at
        )

        logger.info(f"[{pipeline_run_id}] Ingested Source ID: {doc.source_id} (Duplicate: {is_duplicate})")
        self.db.save_source_document(doc)

        if is_duplicate:
            logger.warning(f"[{pipeline_run_id}] Exact duplicate content detected for Source ID {doc.source_id}. Skipping re-extraction.")
            existing_events = [e for e in self.db.get_events_by_source(doc.source_id)]
            return PipelineRunResult(
                pipeline_run_id=pipeline_run_id,
                source_id=doc.source_id,
                events_extracted=[],
                quarantine_records=[],
                total_fragments_processed=0,
                status="SKIPPED_DUPLICATE",
                execution_time_ms=round((time.time() - start_time) * 1000, 2)
            )

        # 2. Content Normalization & Fragmentation
        fragments = self.normalization_service.fragment_document(doc)
        logger.info(f"[{pipeline_run_id}] Created {len(fragments)} fragments for Source ID {doc.source_id}")

        extracted_events = []
        quarantine_records = []

        # 3. Extraction & Structured Validation per Fragment
        for frag in fragments:
            raw_events = self.extraction_service.extract_events_from_fragment(doc, frag)
            for raw_event in raw_events:
                # 4. Validation & Closed-Vocabulary Guardrail (Rule 5)
                validated_event, quarantine_rec = self.validation_service.validate_event(raw_event)

                if quarantine_rec:
                    logger.warning(f"[{pipeline_run_id}] Event {validated_event.event_id} quarantined: {quarantine_rec.quarantine_reasons}")
                    self.db.save_quarantine_record(quarantine_rec)
                    quarantine_records.append(quarantine_rec)

                # Save event to ledger (append-only)
                self.db.save_execution_event(validated_event)
                extracted_events.append(validated_event)

        elapsed_ms = round((time.time() - start_time) * 1000, 2)
        logger.info(f"[{pipeline_run_id}] Completed pipeline for Source {doc.source_id}: {len(extracted_events)} events, {len(quarantine_records)} quarantined ({elapsed_ms} ms)")

        return PipelineRunResult(
            pipeline_run_id=pipeline_run_id,
            source_id=doc.source_id,
            events_extracted=extracted_events,
            quarantine_records=quarantine_records,
            total_fragments_processed=len(fragments),
            status="SUCCESS",
            execution_time_ms=elapsed_ms
        )
