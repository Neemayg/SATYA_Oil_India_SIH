"""
SATYA HITL Review Queue & Validation Decisions API Router Handler (Phase 11)
Delegates planner review queue management and validation decisions to PlannerQueueManager & ValidationService.
Enforces Phase 9 Decision State Snapshot Lock and returns HTTP 409 Conflict on stale state operations.
"""

import threading
import sqlite3
from typing import Dict, Any, Optional
from backend.hitl.queue_manager import PlannerQueueManager
from backend.hitl.validation_service import ValidationService
from backend.models.domain_models import ValidationDecisionType, OverrideReasonCategory
from backend.api.errors import SATYAError
from backend.api.serializers import serialize_planner_queue_item, serialize_validation_decision

class HITLRouteHandler:

    def __init__(self, queue_manager: PlannerQueueManager, validation_service: ValidationService):
        self.queue_manager = queue_manager
        self.validation_service = validation_service
        self._lock = threading.Lock()

    def handle_get_queue(
        self,
        project_id: Optional[str] = None,
        priority: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        GET /api/v1/hitl/queue?project_id=...&priority=...
        Returns prioritized review queue items (P1 > P2 > P3 > P4).
        """
        items = self.queue_manager.get_review_queue(project_id=project_id, priority_filter=priority)
        return {
            "project_id": project_id,
            "priority_filter": priority,
            "count": len(items),
            "queue_items": [serialize_planner_queue_item(item) for item in items]
        }

    def handle_submit_decision(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        POST /api/v1/hitl/decisions
        Payload: {
            event_id, planner_id, decision_type,
            reviewed_trust_version, reviewed_match_result_id, reviewed_evidence_assessment_id,
            selected_activity_id, override_reason_category, reason_notes, requested_evidence_types
        }
        Enforces REST Snapshot Lock and returns 409 Conflict on stale state.
        """
        event_id = payload.get("event_id")
        planner_id = payload.get("planner_id")
        decision_type = payload.get("decision_type")
        reviewed_trust_ver = payload.get("reviewed_trust_version")
        reviewed_match_id = payload.get("reviewed_match_result_id")
        reviewed_evidence_id = payload.get("reviewed_evidence_assessment_id")

        if not event_id or not planner_id or not decision_type or reviewed_trust_ver is None:
            raise SATYAError(
                code="INVALID_PAYLOAD",
                message="Missing required fields: event_id, planner_id, decision_type, reviewed_trust_version.",
                status_code=400
            )

        with self._lock:
            # Snapshot Lock Concurrency Validation
            latest_ta = self.validation_service.db.get_latest_trust_assessment(event_id)
            if not latest_ta:
                raise SATYAError(
                    code="EVENT_NOT_FOUND",
                    message=f"No reviewable trust state found for event '{event_id}'.",
                    status_code=404
                )

            current_trust_version = latest_ta.get("version_index", 1)
            if reviewed_trust_ver != current_trust_version:
                raise SATYAError(
                    code="STALE_REVIEW_STATE",
                    message=f"Planner decision submitted against superseded trust version v{reviewed_trust_ver}. Current version is v{current_trust_version}.",
                    status_code=409,
                    details={
                        "event_id": event_id,
                        "submitted_reviewed_version": reviewed_trust_ver,
                        "current_trust_version": current_trust_version
                    }
                )

            # Delegate decision handling strictly to ValidationService
            try:
                if decision_type == ValidationDecisionType.VALIDATE:
                    decision = self.validation_service.validate_event(
                        event_id=event_id,
                        planner_id=planner_id,
                        reason_notes=payload.get("reason_notes", "")
                    )
                elif decision_type == ValidationDecisionType.CHANGE_MATCH:
                    new_act_id = payload.get("selected_activity_id")
                    if not new_act_id:
                        raise SATYAError(
                            code="INVALID_PAYLOAD",
                            message="selected_activity_id is required for CHANGE_MATCH decisions.",
                            status_code=400
                        )
                    reason_cat = payload.get("override_reason_category", OverrideReasonCategory.OTHER)
                    decision = self.validation_service.change_match(
                        event_id=event_id,
                        new_activity_id=new_act_id,
                        planner_id=planner_id,
                        reason_category=reason_cat,
                        reason_notes=payload.get("reason_notes", "")
                    )
                elif decision_type == ValidationDecisionType.REJECT:
                    decision = self.validation_service.reject_event(
                        event_id=event_id,
                        planner_id=planner_id,
                        reason_notes=payload.get("reason_notes", "")
                    )
                elif decision_type == ValidationDecisionType.REQUEST_EVIDENCE:
                    req_types = payload.get("requested_evidence_types", [])
                    decision = self.validation_service.request_evidence(
                        event_id=event_id,
                        planner_id=planner_id,
                        requested_evidence_types=req_types,
                        reason_notes=payload.get("reason_notes", "")
                    )
                elif decision_type == ValidationDecisionType.DEFER:
                    decision = self.validation_service.defer_event(
                        event_id=event_id,
                        planner_id=planner_id,
                        reason_notes=payload.get("reason_notes", "")
                    )
                else:
                    raise SATYAError(
                        code="INVALID_DECISION_TYPE",
                        message=f"Unsupported decision_type '{decision_type}'.",
                        status_code=400
                    )
            except sqlite3.IntegrityError:
                raise SATYAError(
                    code="STALE_REVIEW_STATE",
                    message=f"Planner decision submitted against superseded trust state.",
                    status_code=409
                )
            except ValueError as ve:
                raise SATYAError(
                    code="INVALID_DECISION_VALUE",
                    message=str(ve),
                    status_code=400
                )

        return serialize_validation_decision(decision)
