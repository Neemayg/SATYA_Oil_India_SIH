import unittest
from backend.validation.event_validator import EventValidationService
from backend.models.domain_models import ExecutionEvent, PipelineState

class TestEventGuardrails(unittest.TestCase):
    def setUp(self):
        self.valid_vocab = {"ACT-1010", "ACT-1011", "ACT-4020"}
        self.validator = EventValidationService(self.valid_vocab)

    def test_rule_5_valid_activity_id_passes(self):
        event = ExecutionEvent(
            event_id="EVT-001", source_id="SRC-001", fragment_id="FRG-001",
            event_type="PROGRESS", observed_timestamp="2026-09-02", source_timestamp="2026-09-02",
            extracted_statement="ACT-1010 400m done.", raw_observed_activity_id="ACT-1010"
        )
        val_event, quarn = self.validator.validate_event(event)
        self.assertIsNone(quarn)
        self.assertEqual(val_event.raw_observed_activity_id, "ACT-1010")
        self.assertEqual(val_event.observed_activity_id, "ACT-1010")
        self.assertEqual(val_event.activity_id_validation_status, "VALID_SCHEDULE_ID")
        self.assertEqual(val_event.lifecycle_state, PipelineState.VALIDATED)

    def test_rule_5_invalid_hallucinated_activity_id_preserves_raw_and_quarantines(self):
        event = ExecutionEvent(
            event_id="EVT-002", source_id="SRC-001", fragment_id="FRG-001",
            event_type="PROGRESS", observed_timestamp="2026-09-02", source_timestamp="2026-09-02",
            extracted_statement="ACT-9999 400m done.", raw_observed_activity_id="ACT-9999"
        )
        val_event, quarn = self.validator.validate_event(event)
        # Observed activity ID reset to None to prevent schedule baseline corruption
        self.assertIsNone(val_event.observed_activity_id)
        # CRITICAL RECOVERY SAFEGUARD: Raw text ID is preserved!
        self.assertEqual(val_event.raw_observed_activity_id, "ACT-9999")
        self.assertEqual(val_event.activity_id_validation_status, "INVALID_EXPLICIT_REFERENCE")
        self.assertIsNotNone(quarn)

    def test_impossible_future_date_quarantined(self):
        event = ExecutionEvent(
            event_id="EVT-003", source_id="SRC-001", fragment_id="FRG-001",
            event_type="PROGRESS", observed_timestamp="2035-12-31", source_timestamp="2026-09-02",
            extracted_statement="Work done in future.", observed_activity_id=None
        )
        val_event, quarn = self.validator.validate_event(event)
        self.assertIsNotNone(quarn)
        self.assertEqual(val_event.lifecycle_state, PipelineState.QUARANTINED)

if __name__ == "__main__":
    unittest.main()
