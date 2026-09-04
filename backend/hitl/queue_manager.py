"""
SATYA Planner Review Queue Manager (Phase 9)
Prioritizes and filters events requiring human planner review based on deterministic precedence rules:
P1_CRITICAL > P2_HIGH > P3_MEDIUM > P4_LOW with deterministic tie-breaking.
"""

import uuid
from typing import List, Optional, Dict, Any
from backend.models.domain_models import (
    QueuePriority, PlannerQueueItem, TrustStatus, MatchOutcome, ConflictSeverity
)
from backend.persistence.database_engine import DatabaseEngine

class PlannerQueueManager:
    """
    Query & Prioritization Engine for Planner HITL Review Queue.
    """

    def __init__(self, db_engine: DatabaseEngine):
        self.db = db_engine

    def get_review_queue(
        self,
        project_id: Optional[str] = None,
        priority_filter: Optional[str] = None,
        discipline_filter: Optional[str] = None
    ) -> List[PlannerQueueItem]:
        """
        Scans all events and persisted trust assessments, identifies actionable items requiring review
        (TrustStatus.REVIEW_REQUIRED or UNTRUSTED or MatchOutcome AMBIGUOUS / INSUFFICIENT_EVIDENCE),
        calculates deterministic priority, applies tie-breaking, and returns ordered queue items.
        """
        all_events = self.db.get_all_execution_events() if not project_id else []
        if project_id:
            # Query documents for project
            with self.db._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT source_id FROM source_documents WHERE project_id = ?", (project_id,))
                source_ids = [row["source_id"] for row in cursor.fetchall()]

            all_events = []
            for sid in source_ids:
                all_events.extend(self.db.get_events_by_source(sid))

        queue_items: List[PlannerQueueItem] = []

        for event_dict in all_events:
            event_id = event_dict["event_id"]

            # Filter by discipline if specified
            if discipline_filter and event_dict.get("discipline", "").upper() != discipline_filter.upper():
                continue

            # Fetch latest trust assessment
            latest_ta = self.db.get_latest_trust_assessment(event_id)
            match_results = self.db.get_match_results_by_event(event_id)
            latest_match = match_results[-1] if match_results else None
            conflicts = self.db.get_conflict_flags_by_event(event_id)

            # Check if event is actionable (requires human attention)
            trust_status = latest_ta["trust_status"] if latest_ta else TrustStatus.REVIEW_REQUIRED
            match_outcome = latest_match["outcome"] if latest_match else MatchOutcome.UNMATCHED

            # TRUSTED events with zero unresolved conflicts are not actionable unless re-opened
            if trust_status == TrustStatus.TRUSTED and not conflicts:
                continue

            # Determine Priority & Trigger Reason
            priority = QueuePriority.P4_LOW
            trigger_reason = latest_ta["gating_trigger"] if latest_ta else "INITIAL_REVIEW"

            has_critical = any(c.get("severity") == ConflictSeverity.CRITICAL for c in conflicts)
            has_high = any(c.get("severity") == ConflictSeverity.HIGH for c in conflicts)

            if has_critical:
                priority = QueuePriority.P1_CRITICAL
                trigger_reason = f"CRITICAL_CONFLICT ({conflicts[0]['conflict_type']})"
            elif has_high or match_outcome == MatchOutcome.AMBIGUOUS:
                priority = QueuePriority.P2_HIGH
                if has_high:
                    trigger_reason = f"HIGH_CONFLICT ({conflicts[0]['conflict_type']})"
                else:
                    trigger_reason = "AMBIGUOUS_MATCH_CANDIDATES"
            elif match_outcome == MatchOutcome.INSUFFICIENT_EVIDENCE or (latest_ta and latest_ta.get("has_evidence_gaps")):
                priority = QueuePriority.P3_MEDIUM
                trigger_reason = "INSUFFICIENT_EVIDENCE_OR_GAPS"
            else:
                priority = QueuePriority.P4_LOW
                trigger_reason = "LOW_MATCH_CONFIDENCE"

            # Filter by priority if specified
            if priority_filter and priority != priority_filter:
                continue

            match_confidence = latest_match["confidence_score"] if latest_match else 0.0
            evidence_support = latest_ta["evidence_support"] if latest_ta else 0.0
            version_idx = latest_ta["version_index"] if latest_ta else 1
            created_at = event_dict.get("source_timestamp", "")

            item = PlannerQueueItem(
                queue_item_id=f"QITEM-{event_id}",
                event_id=event_id,
                project_id=project_id or "PRJ-NBG-2026",
                priority=priority,
                trigger_reason=trigger_reason,
                match_confidence=match_confidence,
                evidence_support=evidence_support,
                latest_trust_version=version_idx,
                created_at=created_at
            )
            queue_items.append(item)

        # Deterministic Sort Order:
        # Priority (P1 < P2 < P3 < P4) -> Ingestion Age (Oldest first) -> Match Confidence (Lowest first) -> Event ID
        priority_order = {
            QueuePriority.P1_CRITICAL: 1,
            QueuePriority.P2_HIGH: 2,
            QueuePriority.P3_MEDIUM: 3,
            QueuePriority.P4_LOW: 4
        }

        queue_items.sort(key=lambda x: (
            priority_order.get(x.priority, 5),
            x.created_at,
            x.match_confidence,
            x.event_id
        ))

        return queue_items
