"""
SATYA Evidence Gap Engine (Phase 8)
Enforces activity-aware and discipline-aware EvidenceRequirementPolicy.
Identifies explicit evidence gaps without making naive universal assumptions.
"""

from typing import List, Optional, Dict, Any
from backend.models.domain_models import (
    ExecutionEvent, Evidence, EvidenceClaim, ActivityFingerprint, ClaimType, CorroborationStatus
)

class EvidenceRequirementPolicy:
    """
    Defines discipline-aware mandatory & optional evidence requirements.
    """
    @staticmethod
    def get_policy(discipline: str) -> Dict[str, Any]:
        disc = discipline.upper() if discipline else "CIVIL"
        if disc in ("PIPING", "MECHANICAL", "QA_QC", "RADIOGRAPHY"):
            return {
                "require_qa_for_completion": True,
                "require_line_or_tag": True,
                "require_independent_corroboration_for_finish": True
            }
        elif disc in ("ELECTRICAL", "INSTRUMENTATION"):
            return {
                "require_qa_for_completion": True,
                "require_line_or_tag": True,
                "require_independent_corroboration_for_finish": False
            }
        else:
            # CIVIL / EARTHWORKS / GENERAL
            return {
                "require_qa_for_completion": False,
                "require_line_or_tag": False,
                "require_independent_corroboration_for_finish": False
            }

class GapEngine:
    """
    Detects evidence gaps for execution events based on claims and activity discipline.
    """

    def detect_gaps(
        self,
        event: ExecutionEvent,
        claims: List[EvidenceClaim],
        evidence_list: List[Evidence],
        corroboration_status: str,
        fingerprint: Optional[ActivityFingerprint] = None
    ) -> List[str]:
        gaps: List[str] = []

        if not evidence_list:
            gaps.append("NO_EVIDENCE_RECORDED")
            return gaps

        discipline = event.discipline or (fingerprint.discipline if fingerprint else "CIVIL")
        policy = EvidenceRequirementPolicy.get_policy(discipline)

        # Extract claims
        progress_claim = next((c for c in claims if c.claim_type in (ClaimType.PROGRESS_CLAIM, ClaimType.STATUS_CLAIM)), None)
        qa_claim = next((c for c in claims if c.claim_type == ClaimType.QA_CLAIM), None)

        is_completion_claim = False
        if progress_claim and progress_claim.normalized_value is not None:
            if progress_claim.normalized_value >= 100.0 or event.event_type == "FINISH":
                is_completion_claim = True

        # 1. Missing QA Clearance Gap (Discipline-Aware)
        if is_completion_claim and policy["require_qa_for_completion"]:
            if not qa_claim or qa_claim.claim_value.get("qa_status") != "PASSED":
                qa_curr = qa_claim.claim_value.get("qa_status") if qa_claim else "NONE"
                gaps.append(f"MISSING_QA_CLEARANCE (Discipline '{discipline}' requires verified QA/NDT clearance for 100% completion claim; current QA status: {qa_curr})")

        # 2. Missing Locator / Spatial Discriminator Gap
        if policy["require_line_or_tag"]:
            has_locator = bool(event.line_number or event.equipment_tag or event.area_location or event.work_front_tag)
            if not has_locator:
                gaps.append(f"MISSING_LOCATOR_PROVENANCE (Discipline '{discipline}' requires line number, equipment tag, or work front locator)")

        # 3. Uncorroborated Major Finish Claim Gap
        if is_completion_claim and policy["require_independent_corroboration_for_finish"]:
            if corroboration_status != CorroborationStatus.CORROBORATED_INDEPENDENT:
                gaps.append(f"UNCORROBORATED_FINISH_CLAIM (Discipline '{discipline}' completion claim supported by only 1 origin group)")

        # 4. Fallback Date Provenance Gap
        if event.temporal_resolution_status == "FALLBACK_SUBMISSION_DATE":
            gaps.append("FALLBACK_DATE_PROVENANCE (Event observed timestamp relies on submission date fallback)")

        return gaps
