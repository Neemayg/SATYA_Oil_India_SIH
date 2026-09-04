"""
SATYA Event Validation & Guardrail Engine
Validates extracted events against schema rules and enforces the Closed-Vocabulary Guardrail (Rule 5).
NEVER FABRICATE OR INVENT ACTIVITY IDs.
Separates extraction validation (VALIDATED) from human execution validation.
"""

import uuid
from datetime import datetime, timezone, timedelta
from typing import Tuple, List, Optional, Set
from backend.models.domain_models import (
    ExecutionEvent, QuarantineRecord, PipelineState, EventType
)

class EventValidationService:
    def __init__(self, valid_activity_vocab: Optional[Set[str]] = None):
        # Set of valid baseline Activity IDs (Closed Vocabulary)
        self.valid_activity_vocab: Set[str] = valid_activity_vocab if valid_activity_vocab else set()

    def set_valid_vocabulary(self, vocab: Set[str]):
        """Sets active schedule Activity ID vocabulary."""
        self.valid_activity_vocab = {act.upper() for act in vocab}

    def validate_event(self, event: ExecutionEvent) -> Tuple[ExecutionEvent, Optional[QuarantineRecord]]:
        """
        Validates ExecutionEvent structure, checks closed-vocabulary Activity IDs,
        and returns (validated_event, quarantine_record_if_failed).
        """
        quarantine_reasons: List[str] = []

        # 1. Closed-Vocabulary Activity ID Guardrail (Rule 5)
        raw_act_id = event.raw_observed_activity_id
        if raw_act_id:
            obs_id = raw_act_id.upper()
            if self.valid_activity_vocab:
                if obs_id not in self.valid_activity_vocab:
                    quarantine_reasons.append(f"Invalid or Unresolved Explicit Activity Reference: '{obs_id}' not found in schedule vocabulary.")
                    event.observed_activity_id = None
                    event.activity_id_validation_status = "INVALID_EXPLICIT_REFERENCE"
                else:
                    event.observed_activity_id = obs_id
                    event.activity_id_validation_status = "VALID_SCHEDULE_ID"
            else:
                event.observed_activity_id = obs_id
                event.activity_id_validation_status = "UNVALIDATED"
        else:
            event.observed_activity_id = None
            event.activity_id_validation_status = "NO_EXPLICIT_REFERENCE"

        # 2. Impossible Date Check (Future Date > 24h)
        if event.observed_timestamp:
            try:
                obs_dt = datetime.strptime(event.observed_timestamp[:10], "%Y-%m-%d")
                now_dt = datetime.now(timezone.utc).replace(tzinfo=None)
                if obs_dt > now_dt + timedelta(days=1):
                    quarantine_reasons.append(f"Impossible Future Date: '{event.observed_timestamp}' is in the future.")
            except Exception:
                quarantine_reasons.append(f"Malformed Date Format: '{event.observed_timestamp}'.")

        # 3. Negative Quantity Check
        if event.observed_quantity is not None and event.observed_quantity < 0:
            quarantine_reasons.append(f"Invalid Negative Quantity: {event.observed_quantity}.")

        # 4. Mandatory Text Check
        if not event.extracted_statement or not event.extracted_statement.strip():
            quarantine_reasons.append("Empty Extracted Statement.")

        # Handle Validation Result
        if quarantine_reasons:
            event.lifecycle_state = PipelineState.QUARANTINED
            event.quarantine_reasons = quarantine_reasons

            quarantine = QuarantineRecord(
                quarantine_id=f"QRN-{uuid.uuid4().hex[:8].upper()}",
                source_id=event.source_id,
                event_id=event.event_id,
                failure_stage="EXTRACTION_VALIDATION",
                quarantine_reasons=quarantine_reasons,
                raw_payload=event.extracted_statement,
                created_at=datetime.now(timezone.utc).isoformat()
            )
            return event, quarantine

        # Extraction Validation Success (Note: NOT Human Execution Validation)
        event.lifecycle_state = PipelineState.VALIDATED
        return event, None
