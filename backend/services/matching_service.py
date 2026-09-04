"""
SATYA Schedule-Aware Activity Matching Service Orchestrator
Coordinates matching ExecutionEvents to cached ActivityFingerprints,
persisting MatchResults to SQLite ledger, and generating explainable reasoning traces.
"""

import json
import logging
from typing import List, Dict, Any, Optional
from backend.models.domain_models import ExecutionEvent, ActivityFingerprint, MatchResult
from backend.matching.matching_engine import ScheduleAwareMatchingEngine
from backend.persistence.database_engine import DatabaseEngine

logger = logging.getLogger("SATYA.Matching")

class ScheduleMatchingService:
    """Service orchestrator for schedule activity matching."""

    def __init__(
        self,
        db_engine: Optional[DatabaseEngine] = None,
        theta_match: float = 0.80,
        theta_unmatched: float = 0.45,
        ambiguity_margin: float = 0.08
    ):
        self.db = db_engine if db_engine else DatabaseEngine(":memory:")
        self.matching_engine = ScheduleAwareMatchingEngine(
            theta_match=theta_match,
            theta_unmatched=theta_unmatched,
            ambiguity_margin=ambiguity_margin
        )

    def match_event(
        self,
        event: ExecutionEvent,
        project_id: Optional[str] = None
    ) -> MatchResult:
        """
        Matches a single ExecutionEvent against indexed ActivityFingerprints in database.
        Persists MatchResult to SQLite database and returns the result.
        """
        if project_id:
            fp_rows = self.db.get_fingerprints_by_project(project_id)
        else:
            fp_rows = self.db.get_all_fingerprints()

        # Reconstruct ActivityFingerprint dataclass instances from DB rows
        fingerprints: List[ActivityFingerprint] = []
        for r in fp_rows:
            fp = ActivityFingerprint(
                fingerprint_id=r["fingerprint_id"],
                activity_id=r["activity_id"],
                project_id=r["project_id"],
                activity_name=r["activity_name"],
                normalized_name=r["normalized_name"],
                wbs_id=r["wbs_id"],
                wbs_code=r["wbs_code"],
                wbs_name_path=r["wbs_name_path"],
                discipline=r["discipline"],
                area_location=r.get("area_location"),
                equipment_tag=r.get("equipment_tag"),
                line_number=r.get("line_number"),
                start_km=r.get("start_km"),
                end_km=r.get("end_km"),
                planned_start=r.get("planned_start"),
                planned_finish=r.get("planned_finish"),
                baseline_duration_days=r.get("baseline_duration_days", 0),
                planned_quantity=r.get("planned_quantity"),
                unit_of_measure=r.get("unit_of_measure"),
                is_critical=bool(r.get("is_critical", 0)),
                predecessors=json.loads(r["predecessors_json"]) if r.get("predecessors_json") else [],
                successors=json.loads(r["successors_json"]) if r.get("successors_json") else [],
                action_verbs=json.loads(r["action_verbs_json"]) if r.get("action_verbs_json") else [],
                entity_nouns=json.loads(r["entity_nouns_json"]) if r.get("entity_nouns_json") else [],
                synonyms=json.loads(r["synonyms_json"]) if r.get("synonyms_json") else [],
                field_aliases=json.loads(r["field_aliases_json"]) if r.get("field_aliases_json") else [],
                search_tokens=json.loads(r["search_tokens_json"]) if r.get("search_tokens_json") else []
            )
            fingerprints.append(fp)

        match_result = self.matching_engine.match_event_to_fingerprints(event, fingerprints)
        self.db.save_match_result(match_result)

        logger.info(f"Matched Event {event.event_id} -> Outcome: {match_result.outcome} (Activity: {match_result.selected_activity_id}, Score: {match_result.confidence_score})")
        return match_result

    def match_events_batch(
        self,
        events: List[ExecutionEvent],
        project_id: Optional[str] = None
    ) -> List[MatchResult]:
        """Matches a list of ExecutionEvents in batch and returns MatchResults."""
        results: List[MatchResult] = []
        for ev in events:
            res = self.match_event(ev, project_id=project_id)
            results.append(res)
        return results
