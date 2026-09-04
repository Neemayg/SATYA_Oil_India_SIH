"""
SATYA Evidence & Trust API Router Handler (Phase 11)
Delegates claim extraction, reliability, corroboration, gap/conflict detection,
and versioned trust evaluation to TrustEvaluatorService.
"""

from typing import Dict, Any
from backend.services.trust_evaluator_service import TrustEvaluatorService
from backend.models.domain_models import ExecutionEvent, MatchResult, MatchOutcome, MatchFactorScores, CandidateMatch
from backend.api.errors import SATYAError
from backend.api.serializers import serialize_trust_assessment

class EvidenceRouteHandler:

    def __init__(self, trust_service: TrustEvaluatorService):
        self.trust_service = trust_service

    def handle_evaluate_trust(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        POST /api/v1/evidence/evaluate
        Payload: {event_id, match_result_id}
        """
        event_id = payload.get("event_id")
        match_result_id = payload.get("match_result_id")

        if not event_id:
            raise SATYAError(
                code="INVALID_PAYLOAD",
                message="Missing required field: event_id.",
                status_code=400
            )

        ev_dict = self.trust_service.db.get_execution_event(event_id)
        if not ev_dict:
            raise SATYAError(
                code="EVENT_NOT_FOUND",
                message=f"Execution event with ID '{event_id}' not found.",
                status_code=404
            )

        event = ExecutionEvent(
            event_id=ev_dict["event_id"],
            source_id=ev_dict["source_id"],
            fragment_id=ev_dict["fragment_id"],
            event_type=ev_dict["event_type"],
            observed_timestamp=ev_dict.get("observed_timestamp"),
            source_timestamp=ev_dict.get("source_timestamp", ""),
            extracted_statement=ev_dict.get("extracted_statement", ""),
            raw_observed_activity_id=ev_dict.get("raw_observed_activity_id"),
            observed_activity_id=ev_dict.get("observed_activity_id"),
            discipline=ev_dict.get("discipline", "UNKNOWN"),
            area_location=ev_dict.get("area_location"),
            equipment_tag=ev_dict.get("equipment_tag"),
            line_number=ev_dict.get("line_number"),
            observed_quantity=ev_dict.get("observed_quantity")
        )

        # Get latest match result for event
        matches = self.trust_service.db.get_match_results_by_event(event_id)
        match_res = None
        source_id = ev_dict.get("source_id", "")
        if matches:
            mr_dict = matches[-1]
            match_res = MatchResult(
                match_id=mr_dict["match_id"],
                event_id=mr_dict["event_id"],
                source_id=source_id,
                outcome=mr_dict.get("outcome", MatchOutcome.UNMATCHED),
                selected_activity_id=mr_dict.get("selected_activity_id"),
                confidence_score=mr_dict.get("confidence_score", 0.0),
                candidate_matches=[],
                evaluated_at=mr_dict.get("evaluated_at", "")
            )
        else:
            match_res = MatchResult(
                match_id="MTH-UNMATCHED",
                event_id=event_id,
                source_id=source_id,
                outcome=MatchOutcome.UNMATCHED,
                selected_activity_id=None,
                confidence_score=0.0,
                candidate_matches=[],
                evaluated_at=""
            )

        trust_assessment = self.trust_service.evaluate_trust_for_event(event, match_res)
        return serialize_trust_assessment(trust_assessment)

    def handle_get_event_trust(self, event_id: str) -> Dict[str, Any]:
        """
        GET /api/v1/evidence/events/{event_id}/trust
        Returns versioned TrustAssessment history.
        """
        history = self.trust_service.db.get_trust_assessments_by_event(event_id)
        if not history:
            raise SATYAError(
                code="TRUST_ASSESSMENT_NOT_FOUND",
                message=f"No trust assessments found for event '{event_id}'.",
                status_code=404
            )
        return {
            "event_id": event_id,
            "version_count": len(history),
            "latest_trust_assessment": history[-1],
            "trust_history": history
        }

    def handle_get_event_conflicts(self, event_id: str) -> Dict[str, Any]:
        """
        GET /api/v1/evidence/events/{event_id}/conflicts
        Returns conflict flags and evidence gaps for an event.
        """
        conflicts = self.trust_service.db.get_conflict_flags_by_event(event_id)
        assessments = self.trust_service.db.get_trust_assessments_by_event(event_id)
        gaps = []
        if assessments:
            latest_ta = assessments[-1]
            gaps = latest_ta.get("rationale_breakdown", {}).get("evidence_gaps", [])

        return {
            "event_id": event_id,
            "conflict_count": len(conflicts),
            "conflicts": conflicts,
            "evidence_gaps": gaps
        }

    def handle_get_event_trace(self, event_id: str) -> Dict[str, Any]:
        """
        GET /api/v1/evidence/events/{event_id}/trace
        Returns complete end-to-end provenance trace: Event -> Claims -> Evidence Fragments -> Source -> Locators -> Trust.
        """
        ev_dict = self.trust_service.db.get_execution_event(event_id)
        if not ev_dict:
            raise SATYAError(
                code="EVENT_NOT_FOUND",
                message=f"Execution event with ID '{event_id}' not found.",
                status_code=404
            )

        source_doc = self.trust_service.db.get_source_document(ev_dict["source_id"])
        evidence = self.trust_service.db.get_evidence_by_event(event_id)
        claims = self.trust_service.db.get_claims_by_event(event_id)
        ea = self.trust_service.db.get_evidence_assessment_by_event(event_id)
        trust_history = self.trust_service.db.get_trust_assessments_by_event(event_id)
        conflicts = self.trust_service.db.get_conflict_flags_by_event(event_id)

        source_info = source_doc.to_dict() if source_doc else None
        latest_ta = trust_history[-1] if trust_history else None

        return {
            "event_id": event_id,
            "execution_event": ev_dict,
            "source_document": source_info,
            "evidence_fragments": evidence,
            "claims": claims,
            "evidence_assessment": ea,
            "latest_trust_assessment": latest_ta,
            "trust_history": trust_history,
            "conflicts": conflicts
        }
