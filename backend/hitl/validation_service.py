"""
SATYA Validation Service (Phase 9)
Service orchestrator executing planner decisions across 5 explicit decision types:
VALIDATE, CHANGE_MATCH, REJECT, REQUEST_EVIDENCE, DEFER.

STRICTLY PROHIBITS mutating past match history or raw observation events.
Enforces closed-vocabulary Rule 5 guardrail validation on CHANGE_MATCH actions.
Appends versioned TrustAssessment records (v(N+1)) and emits PlannerCorrectionRecords.
"""

import uuid
import logging
from datetime import datetime
from typing import List, Optional, Dict, Any, Set

from backend.models.domain_models import (
    ValidationDecision, ValidationDecisionType, TrustStatus, TrustAssessment,
    PlannerCorrectionRecord, OverrideReasonCategory, ExecutionEvent
)
from backend.persistence.database_engine import DatabaseEngine

logger = logging.getLogger("SATYA.ValidationService")

class ValidationService:
    """
    Orchestrates Human Validation decisions and append-only state transitions.
    """

    def __init__(self, db_engine: DatabaseEngine, valid_vocabulary: Optional[Set[str]] = None):
        self.db = db_engine
        self.valid_vocabulary: Set[str] = valid_vocabulary if valid_vocabulary else set()

    def set_valid_vocabulary(self, vocab: Set[str]):
        """Sets active schedule Activity ID vocabulary for Rule 5 validation."""
        self.valid_vocabulary = {v.upper() for v in vocab}

    def _get_active_vocabulary(self) -> Set[str]:
        return self.valid_vocabulary

    def validate_event(
        self,
        event_id: str,
        planner_id: str,
        reason_notes: str = "",
        evidence_reviewed_ids: Optional[List[str]] = None
    ) -> ValidationDecision:
        """
        [VALIDATE]: Planner concurs with machine recommendation & activity match.
        Appends ValidationDecision and new TrustAssessment v(N+1) with status TRUSTED.
        """
        latest_ta = self.db.get_latest_trust_assessment(event_id)
        if not latest_ta:
            raise ValueError(f"No TrustAssessment found for event ID '{event_id}'")

        match_results = self.db.get_match_results_by_event(event_id)
        latest_match = match_results[-1] if match_results else None
        match_id = latest_match["match_id"] if latest_match else "MTH-UNKNOWN"
        selected_act = latest_match["selected_activity_id"] if latest_match else None

        ea_dict = self.db.get_evidence_assessment_by_event(event_id)
        ea_id = ea_dict["assessment_id"] if ea_dict else "EVA-UNKNOWN"

        prev_version = latest_ta["version_index"]
        next_version = prev_version + 1

        # Create ValidationDecision
        decision = ValidationDecision(
            decision_id=f"DEC-{uuid.uuid4().hex[:8].upper()}",
            event_id=event_id,
            planner_id=planner_id,
            decision_type=ValidationDecisionType.VALIDATE,
            reviewed_trust_version=prev_version,
            reviewed_match_result_id=match_id,
            reviewed_evidence_assessment_id=ea_id,
            selected_activity_id=selected_act,
            previous_trust_version=prev_version,
            resulting_trust_version=next_version,
            resulting_trust_status=TrustStatus.TRUSTED,
            override_reason_category=None,
            reason_notes=reason_notes or "Planner validated machine recommendation under policy.",
            evidence_reviewed_ids=evidence_reviewed_ids or [],
            created_at=datetime.now().isoformat()
        )
        self.db.save_validation_decision(decision)

        # Append new versioned TrustAssessment (v(N+1))
        rationale = dict(latest_ta.get("rationale_breakdown", {}))
        rationale["human_validation_note"] = f"Validated by Planner '{planner_id}' at {decision.created_at}"
        rationale["validation_decision_id"] = decision.decision_id

        new_ta = TrustAssessment(
            assessment_id=f"TST-{uuid.uuid4().hex[:8].upper()}",
            event_id=event_id,
            version_index=next_version,
            match_confidence=latest_ta["match_confidence"],
            evidence_support=latest_ta["evidence_support"],
            trust_status=TrustStatus.TRUSTED,
            gating_trigger=f"PLANNER_VALIDATED: Planner '{planner_id}' validated machine match.",
            rationale_breakdown=rationale,
            has_critical_conflict=False,
            has_evidence_gaps=False,
            evaluated_at=datetime.now().isoformat()
        )
        self.db.save_trust_assessment(new_ta)

        logger.info(f"Planner '{planner_id}' VALIDATED Event {event_id} -> TrustAssessment v{next_version} TRUSTED")
        return decision

    def change_match(
        self,
        event_id: str,
        new_activity_id: str,
        planner_id: str,
        reason_category: str = OverrideReasonCategory.TERMINOLOGY_ALIAS,
        reason_notes: str = "",
        evidence_reviewed_ids: Optional[List[str]] = None
    ) -> ValidationDecision:
        """
        [CHANGE_MATCH]: Planner re-maps event to a different valid baseline Activity ID.
        Enforces Rule 5 vocabulary validation.
        Creates ValidationDecision (CHANGE_MATCH), appends TrustAssessment v(N+1) (TRUSTED),
        and emits a derived PlannerCorrectionRecord for Phase 14 Institutional Memory.
        NEVER mutates past MatchResult or ExecutionEvent records.
        """
        new_act_upper = new_activity_id.strip().upper()

        # Rule 5 Closed-Vocabulary Guardrail Validation
        if self.valid_vocabulary and new_act_upper not in self.valid_vocabulary:
            raise ValueError(f"Rule 5 Violation: Target Activity ID '{new_activity_id}' is not present in the ingested schedule baseline vocabulary.")

        latest_ta = self.db.get_latest_trust_assessment(event_id)
        if not latest_ta:
            raise ValueError(f"No TrustAssessment found for event ID '{event_id}'")

        match_results = self.db.get_match_results_by_event(event_id)
        latest_match = match_results[-1] if match_results else None
        match_id = latest_match["match_id"] if latest_match else "MTH-UNKNOWN"
        original_act = latest_match["selected_activity_id"] if latest_match else None

        ea_dict = self.db.get_evidence_assessment_by_event(event_id)
        ea_id = ea_dict["assessment_id"] if ea_dict else "EVA-UNKNOWN"

        prev_version = latest_ta["version_index"]
        next_version = prev_version + 1

        # Create ValidationDecision
        decision = ValidationDecision(
            decision_id=f"DEC-{uuid.uuid4().hex[:8].upper()}",
            event_id=event_id,
            planner_id=planner_id,
            decision_type=ValidationDecisionType.CHANGE_MATCH,
            reviewed_trust_version=prev_version,
            reviewed_match_result_id=match_id,
            reviewed_evidence_assessment_id=ea_id,
            selected_activity_id=new_act_upper,
            previous_trust_version=prev_version,
            resulting_trust_version=next_version,
            resulting_trust_status=TrustStatus.TRUSTED,
            override_reason_category=reason_category,
            reason_notes=reason_notes or f"Re-mapped from '{original_act}' to '{new_act_upper}'",
            evidence_reviewed_ids=evidence_reviewed_ids or [],
            created_at=datetime.now().isoformat()
        )
        self.db.save_validation_decision(decision)

        # Emit derived PlannerCorrectionRecord for Phase 14 Institutional Memory
        correction = PlannerCorrectionRecord(
            correction_id=f"COR-{uuid.uuid4().hex[:8].upper()}",
            event_id=event_id,
            original_activity_id=original_act,
            corrected_activity_id=new_act_upper,
            original_match_result_id=match_id,
            validation_decision_id=decision.decision_id,
            reason_category=reason_category,
            reason_notes=reason_notes,
            planner_id=planner_id,
            created_at=datetime.now().isoformat()
        )
        self.db.save_planner_correction(correction)

        # Append new versioned TrustAssessment (v(N+1))
        rationale = dict(latest_ta.get("rationale_breakdown", {}))
        rationale["human_override"] = True
        rationale["original_activity_id"] = original_act
        rationale["remapped_activity_id"] = new_act_upper
        rationale["override_reason_category"] = reason_category

        new_ta = TrustAssessment(
            assessment_id=f"TST-{uuid.uuid4().hex[:8].upper()}",
            event_id=event_id,
            version_index=next_version,
            match_confidence=1.0,  # Explicit human planner mapping receives 1.0 confidence boost
            evidence_support=latest_ta["evidence_support"],
            trust_status=TrustStatus.TRUSTED,
            gating_trigger=f"PLANNER_CHANGE_MATCH: Re-mapped to Activity '{new_act_upper}' by Planner '{planner_id}'.",
            rationale_breakdown=rationale,
            has_critical_conflict=False,
            has_evidence_gaps=False,
            evaluated_at=datetime.now().isoformat()
        )
        self.db.save_trust_assessment(new_ta)

        logger.info(f"Planner '{planner_id}' CHANGE_MATCH Event {event_id} -> '{new_act_upper}' (TrustAssessment v{next_version} TRUSTED)")
        return decision

    def reject_event(
        self,
        event_id: str,
        planner_id: str,
        reason_category: str = OverrideReasonCategory.SCOPE_EXCLUSION,
        reason_notes: str = "",
        evidence_reviewed_ids: Optional[List[str]] = None
    ) -> ValidationDecision:
        """
        [REJECT]: Planner rejects reported execution claim.
        Appends ValidationDecision and new TrustAssessment v(N+1) with status UNTRUSTED.
        """
        latest_ta = self.db.get_latest_trust_assessment(event_id)
        if not latest_ta:
            raise ValueError(f"No TrustAssessment found for event ID '{event_id}'")

        match_results = self.db.get_match_results_by_event(event_id)
        latest_match = match_results[-1] if match_results else None
        match_id = latest_match["match_id"] if latest_match else "MTH-UNKNOWN"

        ea_dict = self.db.get_evidence_assessment_by_event(event_id)
        ea_id = ea_dict["assessment_id"] if ea_dict else "EVA-UNKNOWN"

        prev_version = latest_ta["version_index"]
        next_version = prev_version + 1

        decision = ValidationDecision(
            decision_id=f"DEC-{uuid.uuid4().hex[:8].upper()}",
            event_id=event_id,
            planner_id=planner_id,
            decision_type=ValidationDecisionType.REJECT,
            reviewed_trust_version=prev_version,
            reviewed_match_result_id=match_id,
            reviewed_evidence_assessment_id=ea_id,
            selected_activity_id=None,
            previous_trust_version=prev_version,
            resulting_trust_version=next_version,
            resulting_trust_status=TrustStatus.UNTRUSTED,
            override_reason_category=reason_category,
            reason_notes=reason_notes or "Rejected by planner review.",
            evidence_reviewed_ids=evidence_reviewed_ids or [],
            created_at=datetime.now().isoformat()
        )
        self.db.save_validation_decision(decision)

        new_ta = TrustAssessment(
            assessment_id=f"TST-{uuid.uuid4().hex[:8].upper()}",
            event_id=event_id,
            version_index=next_version,
            match_confidence=latest_ta["match_confidence"],
            evidence_support=latest_ta["evidence_support"],
            trust_status=TrustStatus.UNTRUSTED,
            gating_trigger=f"PLANNER_REJECTED: Rejected by Planner '{planner_id}' ({reason_category}).",
            rationale_breakdown={"rejection_reason": reason_notes, "category": reason_category},
            has_critical_conflict=latest_ta.get("has_critical_conflict", False),
            has_evidence_gaps=latest_ta.get("has_evidence_gaps", False),
            evaluated_at=datetime.now().isoformat()
        )
        self.db.save_trust_assessment(new_ta)

        logger.info(f"Planner '{planner_id}' REJECTED Event {event_id} -> TrustAssessment v{next_version} UNTRUSTED")
        return decision

    def request_evidence(
        self,
        event_id: str,
        planner_id: str,
        reason_notes: str = "",
        evidence_reviewed_ids: Optional[List[str]] = None
    ) -> ValidationDecision:
        """
        [REQUEST_EVIDENCE]: Planner flags event back to site for missing locators/proof.
        Represents "insufficient information to conclude yet". Keeps status REVIEW_REQUIRED.
        """
        latest_ta = self.db.get_latest_trust_assessment(event_id)
        if not latest_ta:
            raise ValueError(f"No TrustAssessment found for event ID '{event_id}'")

        match_results = self.db.get_match_results_by_event(event_id)
        latest_match = match_results[-1] if match_results else None
        match_id = latest_match["match_id"] if latest_match else "MTH-UNKNOWN"

        ea_dict = self.db.get_evidence_assessment_by_event(event_id)
        ea_id = ea_dict["assessment_id"] if ea_dict else "EVA-UNKNOWN"

        prev_version = latest_ta["version_index"]
        next_version = prev_version + 1

        decision = ValidationDecision(
            decision_id=f"DEC-{uuid.uuid4().hex[:8].upper()}",
            event_id=event_id,
            planner_id=planner_id,
            decision_type=ValidationDecisionType.REQUEST_EVIDENCE,
            reviewed_trust_version=prev_version,
            reviewed_match_result_id=match_id,
            reviewed_evidence_assessment_id=ea_id,
            selected_activity_id=latest_match["selected_activity_id"] if latest_match else None,
            previous_trust_version=prev_version,
            resulting_trust_version=next_version,
            resulting_trust_status=TrustStatus.REVIEW_REQUIRED,
            override_reason_category=None,
            reason_notes=reason_notes or "Evidence requested from site supervisor.",
            evidence_reviewed_ids=evidence_reviewed_ids or [],
            created_at=datetime.now().isoformat()
        )
        self.db.save_validation_decision(decision)

        # Keeps status REVIEW_REQUIRED (workflow decision, not negative truth decision)
        new_ta = TrustAssessment(
            assessment_id=f"TST-{uuid.uuid4().hex[:8].upper()}",
            event_id=event_id,
            version_index=next_version,
            match_confidence=latest_ta["match_confidence"],
            evidence_support=latest_ta["evidence_support"],
            trust_status=TrustStatus.REVIEW_REQUIRED,
            gating_trigger=f"EVIDENCE_REQUESTED: Planner '{planner_id}' requested additional evidence.",
            rationale_breakdown=dict(latest_ta.get("rationale_breakdown", {})),
            has_critical_conflict=latest_ta.get("has_critical_conflict", False),
            has_evidence_gaps=True,
            evaluated_at=datetime.now().isoformat()
        )
        self.db.save_trust_assessment(new_ta)

        logger.info(f"Planner '{planner_id}' REQUEST_EVIDENCE for Event {event_id}")
        return decision

    def defer_event(
        self,
        event_id: str,
        planner_id: str,
        reason_notes: str = "",
        evidence_reviewed_ids: Optional[List[str]] = None
    ) -> ValidationDecision:
        """
        [DEFER]: Planner postpones decision for shift handoff / senior review.
        Appends ValidationDecision (DEFER), keeps event in queue with status REVIEW_REQUIRED.
        Does NOT manufacture a new false trust conclusion.
        """
        latest_ta = self.db.get_latest_trust_assessment(event_id)
        if not latest_ta:
            raise ValueError(f"No TrustAssessment found for event ID '{event_id}'")

        match_results = self.db.get_match_results_by_event(event_id)
        latest_match = match_results[-1] if match_results else None
        match_id = latest_match["match_id"] if latest_match else "MTH-UNKNOWN"

        ea_dict = self.db.get_evidence_assessment_by_event(event_id)
        ea_id = ea_dict["assessment_id"] if ea_dict else "EVA-UNKNOWN"

        prev_version = latest_ta["version_index"]
        # Deferral keeps current trust version or appends decision record without changing trust conclusion
        next_version = prev_version + 1

        decision = ValidationDecision(
            decision_id=f"DEC-{uuid.uuid4().hex[:8].upper()}",
            event_id=event_id,
            planner_id=planner_id,
            decision_type=ValidationDecisionType.DEFER,
            reviewed_trust_version=prev_version,
            reviewed_match_result_id=match_id,
            reviewed_evidence_assessment_id=ea_id,
            selected_activity_id=latest_match["selected_activity_id"] if latest_match else None,
            previous_trust_version=prev_version,
            resulting_trust_version=next_version,
            resulting_trust_status=TrustStatus.REVIEW_REQUIRED,
            override_reason_category=None,
            reason_notes=reason_notes or "Deferred for senior planner review.",
            evidence_reviewed_ids=evidence_reviewed_ids or [],
            created_at=datetime.now().isoformat()
        )
        self.db.save_validation_decision(decision)

        # Deferral appends decision but keeps existing trust status & trigger intact
        new_ta = TrustAssessment(
            assessment_id=f"TST-{uuid.uuid4().hex[:8].upper()}",
            event_id=event_id,
            version_index=next_version,
            match_confidence=latest_ta["match_confidence"],
            evidence_support=latest_ta["evidence_support"],
            trust_status=TrustStatus.REVIEW_REQUIRED,
            gating_trigger=f"PLANNER_DEFERRED: Review deferred by Planner '{planner_id}'.",
            rationale_breakdown=dict(latest_ta.get("rationale_breakdown", {})),
            has_critical_conflict=latest_ta.get("has_critical_conflict", False),
            has_evidence_gaps=latest_ta.get("has_evidence_gaps", False),
            evaluated_at=datetime.now().isoformat()
        )
        self.db.save_trust_assessment(new_ta)

        logger.info(f"Planner '{planner_id}' DEFERRED Event {event_id}")
        return decision
