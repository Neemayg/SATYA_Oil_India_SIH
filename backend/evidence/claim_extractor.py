"""
SATYA Evidence Claim Extractor (Phase 8)
Decomposes ExecutionEvent and SourceFragment records into atomic EvidenceClaim instances.
Single fragments can support multiple claims (Status, Quantity, Progress, QA, Location, Temporal).
"""

import uuid
from typing import List, Optional, Dict, Any
from backend.models.domain_models import (
    ExecutionEvent, SourceFragment, Evidence, EvidenceClaim, ClaimType
)

class ClaimExtractor:
    """
    Decomposes an ExecutionEvent and associated Evidence record into atomic claims.
    """

    def extract_claims(self, event: ExecutionEvent, evidence: Evidence) -> List[EvidenceClaim]:
        claims: List[EvidenceClaim] = []

        # 1. Progress / Status Claim
        if event.progress_percent is not None or event.status_text or event.event_type:
            raw_stmt = f"Reported progress: {event.progress_percent}%" if event.progress_percent is not None else (event.status_text or event.event_type)
            claim_val = {
                "progress_percent": event.progress_percent,
                "status_text": event.status_text,
                "event_type": event.event_type
            }
            claims.append(EvidenceClaim(
                claim_id=f"CLM-{uuid.uuid4().hex[:8].upper()}",
                evidence_id=evidence.evidence_id,
                event_id=event.event_id,
                claim_type=ClaimType.PROGRESS_CLAIM if event.progress_percent is not None else ClaimType.STATUS_CLAIM,
                raw_statement=raw_stmt,
                claim_value=claim_val,
                unit="PERCENT" if event.progress_percent is not None else None,
                normalized_value=event.progress_percent,
                confidence=event.extraction_confidence
            ))

        # 2. Quantity Claim
        if event.observed_quantity is not None and event.observed_quantity > 0:
            claims.append(EvidenceClaim(
                claim_id=f"CLM-{uuid.uuid4().hex[:8].upper()}",
                evidence_id=evidence.evidence_id,
                event_id=event.event_id,
                claim_type=ClaimType.QUANTITY_CLAIM,
                raw_statement=f"Reported quantity: {event.observed_quantity} {event.unit_of_measure or ''}".strip(),
                claim_value={"observed_quantity": event.observed_quantity, "unit": event.unit_of_measure},
                unit=event.unit_of_measure,
                normalized_value=float(event.observed_quantity),
                confidence=event.extraction_confidence
            ))

        # 3. QA / Inspection Clearance Claim
        # Check explicit pending_qa_clearance flag or text indicators in status_text/statement
        raw_statement_lower = event.extracted_statement.lower()
        qa_status = None
        if "qa rejected" in raw_statement_lower or "failed inspection" in raw_statement_lower or "ndt failed" in raw_statement_lower:
            qa_status = "REJECTED"
        elif "qa approved" in raw_statement_lower or "qa cleared" in raw_statement_lower or "ndt passed" in raw_statement_lower or "inspection cleared" in raw_statement_lower:
            qa_status = "PASSED"
        elif event.pending_qa_clearance or "qa pending" in raw_statement_lower or "inspection pending" in raw_statement_lower or "ndt pending" in raw_statement_lower:
            qa_status = "PENDING"
        elif event.event_type in ("QA_CLEARANCE", "INSPECTION"):
            qa_status = "PASSED"

        if qa_status:
            claims.append(EvidenceClaim(
                claim_id=f"CLM-{uuid.uuid4().hex[:8].upper()}",
                evidence_id=evidence.evidence_id,
                event_id=event.event_id,
                claim_type=ClaimType.QA_CLAIM,
                raw_statement=f"QA/Inspection Status: {qa_status}",
                claim_value={"qa_status": qa_status, "pending_qa_clearance": event.pending_qa_clearance},
                unit=None,
                normalized_value=1.0 if qa_status == "PASSED" else (0.0 if qa_status == "REJECTED" else 0.5),
                confidence=event.extraction_confidence
            ))

        # 4. Location / Spatial Claim
        loc_parts = []
        if event.area_location:
            loc_parts.append(f"Area: {event.area_location}")
        if event.line_number:
            loc_parts.append(f"Line: {event.line_number}")
        if event.equipment_tag:
            loc_parts.append(f"Tag: {event.equipment_tag}")
        if event.work_front_tag:
            loc_parts.append(f"Front: {event.work_front_tag}")

        if loc_parts:
            claims.append(EvidenceClaim(
                claim_id=f"CLM-{uuid.uuid4().hex[:8].upper()}",
                evidence_id=evidence.evidence_id,
                event_id=event.event_id,
                claim_type=ClaimType.LOCATION_CLAIM,
                raw_statement=", ".join(loc_parts),
                claim_value={
                    "area_location": event.area_location,
                    "line_number": event.line_number,
                    "equipment_tag": event.equipment_tag,
                    "work_front_tag": event.work_front_tag
                },
                unit=None,
                normalized_value=None,
                confidence=event.extraction_confidence
            ))

        # 5. Temporal Claim
        if event.observed_timestamp:
            claims.append(EvidenceClaim(
                claim_id=f"CLM-{uuid.uuid4().hex[:8].upper()}",
                evidence_id=evidence.evidence_id,
                event_id=event.event_id,
                claim_type=ClaimType.TEMPORAL_CLAIM,
                raw_statement=f"Observed Date: {event.observed_timestamp}",
                claim_value={
                    "observed_timestamp": event.observed_timestamp,
                    "source_timestamp": event.source_timestamp,
                    "temporal_resolution_status": event.temporal_resolution_status
                },
                unit="ISO_DATE",
                normalized_value=None,
                confidence=event.extraction_confidence
            ))

        return claims
