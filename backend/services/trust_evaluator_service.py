"""
SATYA Trust Evaluator Service (Phase 8)
Orchestrates ScheduleMatchingService, ClaimExtractor, ReliabilityEvaluator,
CorroborationEngine, GapEngine, and ConflictEngine.

Applies a deterministic Gating Tree (no opaque weighted formula) to evaluate TrustStatus:
TRUSTED, REVIEW_REQUIRED, UNTRUSTED.

Persists append-only versioned TrustAssessment records (v1, v2, etc.).
"""

import uuid
import logging
from datetime import datetime
from typing import List, Optional, Dict, Any

from backend.models.domain_models import (
    ExecutionEvent, SourceDocument, SourceFragment, MatchResult,
    Evidence, EvidenceClaim, EvidenceReliabilityAssessment, EvidenceAssessment,
    ConflictFlag, TrustStatus, TrustAssessment, ConflictSeverity, ActivityFingerprint
)
from backend.persistence.database_engine import DatabaseEngine
from backend.evidence.claim_extractor import ClaimExtractor
from backend.evidence.reliability_evaluator import ReliabilityEvaluator
from backend.evidence.corroboration_engine import CorroborationEngine
from backend.evidence.gap_engine import GapEngine
from backend.evidence.conflict_engine import ConflictEngine

logger = logging.getLogger("SATYA.TrustEvaluator")

class TrustEvaluatorService:
    """
    Service orchestrator evaluating Evidence, Claims, Corroboration, Gaps, Conflicts,
    and Trust Decisions across the Execution Truth Layer.
    """

    def __init__(
        self,
        db_engine: DatabaseEngine,
        default_match_threshold: float = 0.75,
        default_evidence_threshold: float = 0.60
    ):
        self.db = db_engine
        # Initial policy defaults (explicitly configurable heuristics)
        self.DEFAULT_MATCH_THRESHOLD = default_match_threshold
        self.DEFAULT_EVIDENCE_THRESHOLD = default_evidence_threshold

        self.claim_extractor = ClaimExtractor()
        self.reliability_evaluator = ReliabilityEvaluator()
        self.corroboration_engine = CorroborationEngine()
        self.gap_engine = GapEngine()
        self.conflict_engine = ConflictEngine()

    def evaluate_trust_for_event(
        self,
        event: ExecutionEvent,
        match_result: MatchResult,
        source_doc: Optional[SourceDocument] = None,
        source_fragment: Optional[SourceFragment] = None,
        fingerprint: Optional[ActivityFingerprint] = None,
        additional_evidence: Optional[List[Evidence]] = None,
        create_primary_evidence: bool = True
    ) -> TrustAssessment:
        """
        Processes an ExecutionEvent, creates Evidence & Claims, evaluates Corroboration,
        Gaps, and Conflicts, applies the Deterministic Gating Tree, and saves a versioned TrustAssessment.
        """
        all_evidence: List[Evidence] = []
        if create_primary_evidence:
            primary_evidence = Evidence(
                evidence_id=f"EVD-{uuid.uuid4().hex[:8].upper()}",
                event_id=event.event_id,
                source_id=event.source_id,
                fragment_id=event.fragment_id,
                locator_type=source_fragment.locator_type if source_fragment else "TEXT_SPAN",
                locator_value=source_fragment.locator_value if source_fragment else "Document text",
                source_type=source_doc.source_type if source_doc else "TEXT_DOCUMENT",
                origin_group_id=source_doc.source_id if source_doc else event.source_id,
                raw_text_snippet=event.extracted_statement,
                observed_timestamp=event.observed_timestamp,
                provenance_map=event.provenance.field_provenance_map if event.provenance else {},
                created_at=datetime.now().isoformat()
            )
            self.db.save_evidence(primary_evidence)
            all_evidence.append(primary_evidence)

        if additional_evidence:
            all_evidence.extend(additional_evidence)

        # 2. Extract Claims
        all_claims: List[EvidenceClaim] = []
        for ev in all_evidence:
            extracted_claims = self.claim_extractor.extract_claims(event, ev)
            for c in extracted_claims:
                self.db.save_evidence_claim(c)
                all_claims.append(c)

        # 3. Evaluate Evidence Reliability
        reliability_assessments: List[EvidenceReliabilityAssessment] = []
        for ev in all_evidence:
            rel = self.reliability_evaluator.evaluate_reliability(ev, source_doc)
            reliability_assessments.append(rel)

        # 4. Evaluate Corroboration
        evidence_assessment = self.corroboration_engine.evaluate_corroboration(
            event_id=event.event_id,
            evidence_list=all_evidence,
            claim_list=all_claims,
            reliability_list=reliability_assessments
        )

        # 5. Detect Evidence Gaps
        evidence_gaps = self.gap_engine.detect_gaps(
            event=event,
            claims=all_claims,
            evidence_list=all_evidence,
            corroboration_status=evidence_assessment.corroboration_status,
            fingerprint=fingerprint
        )
        evidence_assessment.evidence_gaps = evidence_gaps
        self.db.save_evidence_assessment(evidence_assessment)

        # 6. Detect Conflicts
        # Fetch historical events/claims for same project/activity
        historical_events: List[ExecutionEvent] = []
        conflicts = self.conflict_engine.detect_conflicts(
            target_event=event,
            target_claims=all_claims,
            target_evidence=all_evidence,
            historical_events=historical_events,
            historical_claims=[],
            fingerprint=fingerprint
        )

        for cnf in conflicts:
            self.db.save_conflict_flag(cnf)

        has_critical_conflict = any(c.severity in (ConflictSeverity.CRITICAL, ConflictSeverity.HIGH) for c in conflicts)
        has_evidence_gaps = len(evidence_gaps) > 0

        # 7. Apply Deterministic Gating Tree
        match_confidence = match_result.confidence_score if match_result else 0.0
        evidence_support = evidence_assessment.evidence_support_score

        # GATING TREE EVALUATION
        if not all_evidence or len(all_evidence) == 0:
            trust_status = TrustStatus.UNTRUSTED
            gating_trigger = "ZERO_EVIDENCE_RECORDED: High match score does not compensate for absence of evidence."
        elif match_confidence < self.DEFAULT_MATCH_THRESHOLD:
            trust_status = TrustStatus.UNTRUSTED
            gating_trigger = f"INSUFFICIENT_SCHEDULE_MATCH: Match confidence {match_confidence:.2f} below default threshold {self.DEFAULT_MATCH_THRESHOLD:.2f}"
        elif has_critical_conflict:
            trust_status = TrustStatus.REVIEW_REQUIRED
            gating_trigger = f"BLOCKING_CONFLICT_PRESENT: Severe conflict detected ({conflicts[0].conflict_type})"
        elif evidence_support < self.DEFAULT_EVIDENCE_THRESHOLD:
            trust_status = TrustStatus.REVIEW_REQUIRED
            gating_trigger = f"INSUFFICIENT_EVIDENCE_SUPPORT: Support score {evidence_support:.2f} below threshold {self.DEFAULT_EVIDENCE_THRESHOLD:.2f}"
        elif has_evidence_gaps:
            trust_status = TrustStatus.REVIEW_REQUIRED
            gating_trigger = f"MANDATORY_EVIDENCE_GAP: Unresolved gap '{evidence_gaps[0]}'"
        else:
            trust_status = TrustStatus.TRUSTED
            gating_trigger = "EVIDENCE_SUFFICIENT_AND_CONSISTENT: Claim satisfies configured trust policy defaults."

        # 8. Append-Only Version Index Resolution
        latest_ta = self.db.get_latest_trust_assessment(event.event_id)
        next_version = (latest_ta["version_index"] + 1) if latest_ta else 1

        rationale_breakdown = {
            "schedule_match_confidence": f"{match_confidence * 100:.1f}%",
            "evidence_support_score": f"{evidence_support * 100:.1f}%",
            "source_reliability_tier": reliability_assessments[0].reliability_tier if reliability_assessments else "UNKNOWN",
            "corroboration_status": evidence_assessment.corroboration_status,
            "unique_origin_count": evidence_assessment.unique_origin_count,
            "conflicts_detected_count": len(conflicts),
            "evidence_gaps_count": len(evidence_gaps),
            "gating_trigger": gating_trigger,
            "trust_policy_note": "TRUSTED status means trusted under configured SATYA policy, NOT physically proven."
        }

        trust_assessment = TrustAssessment(
            assessment_id=f"TST-{uuid.uuid4().hex[:8].upper()}",
            event_id=event.event_id,
            version_index=next_version,
            match_confidence=match_confidence,
            evidence_support=evidence_support,
            trust_status=trust_status,
            gating_trigger=gating_trigger,
            rationale_breakdown=rationale_breakdown,
            has_critical_conflict=has_critical_conflict,
            has_evidence_gaps=has_evidence_gaps,
            evaluated_at=datetime.now().isoformat()
        )

        self.db.save_trust_assessment(trust_assessment)
        logger.info(f"Trust Assessment v{next_version} for Event {event.event_id} -> {trust_status} ({gating_trigger})")

        return trust_assessment
