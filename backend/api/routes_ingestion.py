"""
SATYA Ingestion API Router Handler (Phase 11)
Delegates document and raw text payload ingestion to ExecutionEventPipelineService.
Does NOT create duplicate domain logic inside route handlers.
"""

from typing import Dict, Any
from backend.services.pipeline_service import ExecutionEventPipelineService
from backend.api.errors import SATYAError
from backend.api.serializers import serialize_source_bounded, serialize_execution_event

class IngestionRouteHandler:

    def __init__(self, pipeline_service: ExecutionEventPipelineService):
        self.pipeline_service = pipeline_service

    def handle_upload(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        POST /api/v1/ingestion/upload
        Payload: {project_id, source_type, file_name, content, observed_timestamp}
        """
        project_id = payload.get("project_id")
        content = payload.get("content")
        source_type = payload.get("source_type", "TEXT_DOCUMENT")
        file_name = payload.get("file_name", "dpr_upload.txt")
        observed_ts = payload.get("observed_timestamp")

        if not project_id or not content:
            raise SATYAError(
                code="INVALID_PAYLOAD",
                message="Missing required fields: project_id and content are required.",
                status_code=400
            )

        run_res = self.pipeline_service.process_source_payload(
            raw_content=content,
            project_id=project_id,
            source_type=source_type,
            file_name=file_name,
            author="API_Client",
            submitted_at=observed_ts
        )

        try:
            db = self.pipeline_service.db
            from backend.services.matching_service import ScheduleMatchingService
            from backend.services.trust_evaluator_service import TrustEvaluatorService
            from backend.projection.projection_service import ScheduleProjectionService

            matching_svc = ScheduleMatchingService(db)
            trust_svc = TrustEvaluatorService(db)
            proj_svc = ScheduleProjectionService(db)

            for ev in run_res.events_extracted:
                matching_svc.match_event(ev)
                trust_svc.evaluate_trust(ev.event_id)

            proj_svc.generate_projection_for_project(project_id)
        except Exception as e:
            pass

        return {
            "pipeline_run_id": run_res.pipeline_run_id,
            "source_id": run_res.source_id,
            "status": run_res.status,
            "events_extracted_count": len(run_res.events_extracted),
            "events_extracted": [serialize_execution_event(ev) for ev in run_res.events_extracted],
            "quarantined_count": len(run_res.quarantine_records),
            "execution_time_ms": run_res.execution_time_ms
        }

    def handle_get_source(self, source_id: str) -> Dict[str, Any]:
        """
        GET /api/v1/ingestion/sources/{source_id}
        Returns bounded source metadata + extracted event IDs summary.
        """
        doc = self.pipeline_service.db.get_source_document(source_id)
        if not doc:
            raise SATYAError(
                code="SOURCE_NOT_FOUND",
                message=f"Source document with ID '{source_id}' not found.",
                status_code=404
            )

        events = self.pipeline_service.db.get_events_by_source(source_id)
        event_ids = [ev["event_id"] for ev in events]

        return serialize_source_bounded(doc, event_ids)

    def handle_get_event(self, event_id: str) -> Dict[str, Any]:
        """
        GET /api/v1/ingestion/events/{event_id}
        Returns detailed ExecutionEvent record with provenance spans.
        """
        ev_dict = self.pipeline_service.db.get_execution_event(event_id)
        if not ev_dict:
            raise SATYAError(
                code="EVENT_NOT_FOUND",
                message=f"Execution event with ID '{event_id}' not found.",
                status_code=404
            )
        return ev_dict
