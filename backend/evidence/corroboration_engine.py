"""
SATYA Evidence Corroboration Engine (Phase 8)
Evaluates corroboration across multiple evidence items supporting an execution event.
Enforces origin_group_id separation so re-quoted reports from the same origin
do NOT receive independent corroboration credit.
"""

import uuid
from typing import List, Optional, Dict, Any, Set
from backend.models.domain_models import (
    Evidence, EvidenceClaim, EvidenceReliabilityAssessment, CorroborationStatus, EvidenceAssessment
)

class CorroborationEngine:
    """
    Evaluates evidence corroboration, unique origin counts, and overall evidence support score.
    """

    def evaluate_corroboration(
        self,
        event_id: str,
        evidence_list: List[Evidence],
        claim_list: List[EvidenceClaim],
        reliability_list: List[EvidenceReliabilityAssessment]
    ) -> EvidenceAssessment:
        reasoning: List[str] = []

        if not evidence_list:
            reasoning.append("Corroboration: Zero evidence items provided (UNMATCHED / UNTESTED)")
            return EvidenceAssessment(
                assessment_id=f"EVA-{uuid.uuid4().hex[:8].upper()}",
                event_id=event_id,
                evidence_ids=[],
                claim_ids=[],
                corroboration_status=CorroborationStatus.UNCORROBORATED,
                unique_origin_count=0,
                evidence_support_score=0.0,
                reliability_assessments=[],
                evidence_gaps=["NO_EVIDENCE_RECORDED"],
                reasoning_trace=reasoning,
                evaluated_at=""
            )

        evidence_ids = [e.evidence_id for e in evidence_list]
        claim_ids = [c.claim_id for c in claim_list]

        # Extract unique origin groups
        origin_groups: Set[str] = {e.origin_group_id for e in evidence_list if e.origin_group_id}
        unique_origin_count = len(origin_groups)

        # Calculate average reliability score
        if reliability_list:
            avg_reliability = sum(r.overall_reliability_score for r in reliability_list) / len(reliability_list)
        else:
            avg_reliability = 0.50

        # Determine Corroboration Status & Support Score
        if len(evidence_list) <= 1 or unique_origin_count <= 1:
            if len(evidence_list) > 1:
                status = CorroborationStatus.CORROBORATED_SAME_ORIGIN
                corrob_boost = 0.05  # Slight boost for multiple fragments from same source
                reasoning.append(f"Corroboration: Same Origin ({len(evidence_list)} items from 1 origin group '{list(origin_groups)[0] if origin_groups else 'DEFAULT'}')")
            else:
                status = CorroborationStatus.UNCORROBORATED
                corrob_boost = 0.0
                reasoning.append("Corroboration: Uncorroborated (Single evidence source)")
        else:
            status = CorroborationStatus.CORROBORATED_INDEPENDENT
            # Independent corroboration boost (+0.25 for 2 independent sources, +0.35 for 3+)
            corrob_boost = 0.25 if unique_origin_count == 2 else 0.35
            reasoning.append(f"Corroboration: Independent Corroboration ({unique_origin_count} distinct origin groups: {sorted(list(origin_groups))})")

        # Compute Evidence Support Score S_evidence in [0.0, 1.0]
        # Base score is driven by average reliability + corroboration boost
        evidence_support_score = round(min(1.0, avg_reliability * 0.70 + corrob_boost + 0.15), 4)

        reasoning.insert(0, f"Evidence Support Score S_evidence: {evidence_support_score:.2f} (Status: {status})")

        return EvidenceAssessment(
            assessment_id=f"EVA-{uuid.uuid4().hex[:8].upper()}",
            event_id=event_id,
            evidence_ids=evidence_ids,
            claim_ids=claim_ids,
            corroboration_status=status,
            unique_origin_count=unique_origin_count,
            evidence_support_score=evidence_support_score,
            reliability_assessments=reliability_list,
            evidence_gaps=[],
            reasoning_trace=reasoning,
            evaluated_at=""
        )
