"""
SATYA Schedule Matching API Router Handler (Phase 11)
Delegates 2-stage candidate matching execution to ScheduleMatchingService.
"""

from typing import Dict, Any
from backend.services.matching_service import ScheduleMatchingService
from backend.models.domain_models import ExecutionEvent
from backend.api.errors import SATYAError
from backend.api.serializers import serialize_match_result

class MatchingRouteHandler:

    def __init__(self, matching_service: ScheduleMatchingService):
        self.matching_service = matching_service

    def handle_match_event(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        POST /api/v1/matching/match
        Payload: {event_id}
        """
        event_id = payload.get("event_id")
        if not event_id:
            raise SATYAError(
                code="INVALID_PAYLOAD",
                message="Missing required field: event_id.",
                status_code=400
            )

        ev_dict = self.matching_service.db.get_execution_event(event_id)
        if not ev_dict:
            raise SATYAError(
                code="EVENT_NOT_FOUND",
                message=f"Execution event with ID '{event_id}' not found.",
                status_code=404
            )

        # Reconstruct ExecutionEvent domain object
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

        match_res = self.matching_service.match_event(event)
        return serialize_match_result(match_res)

    def handle_get_event_matches(self, event_id: str) -> Dict[str, Any]:
        """
        GET /api/v1/matching/events/{event_id}
        """
        matches = self.matching_service.db.get_match_results_by_event(event_id)
        if not matches:
            raise SATYAError(
                code="MATCH_NOT_FOUND",
                message=f"No match results found for event '{event_id}'.",
                status_code=404
            )
        return {
            "event_id": event_id,
            "count": len(matches),
            "match_results": matches
        }
