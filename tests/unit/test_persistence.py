import unittest
from backend.persistence.database_engine import DatabaseEngine
from backend.models.domain_models import (
    SourceDocument, ExecutionEvent, ProvenanceRecord, QuarantineRecord,
    SourceType, PipelineState, EventType
)

class TestDatabasePersistence(unittest.TestCase):
    def setUp(self):
        self.db = DatabaseEngine(":memory:")

    def test_save_and_retrieve_source_and_event(self):
        doc = SourceDocument(
            source_id="SRC-1001", project_id="PRJ-NBG-2026", source_type=SourceType.DPR_EXCEL,
            file_name="dpr.xlsx", sha256_hash="hash12345", raw_content="Raw DPR Content",
            submitted_at="2026-09-02T10:00:00Z", received_at="2026-09-02T10:00:00Z"
        )
        self.db.save_source_document(doc)

        prov = ProvenanceRecord(
            provenance_id="PRV-001", event_id="EVT-001", source_id=doc.source_id,
            source_type=doc.source_type, locator_type="EXCEL_CELL", locator_value="Sheet1!R12",
            raw_text_snippet="ACT-1010 400m done."
        )

        event = ExecutionEvent(
            event_id="EVT-001", source_id=doc.source_id, fragment_id="FRG-001",
            event_type=EventType.PROGRESS, observed_timestamp="2026-09-02",
            source_timestamp=doc.submitted_at, extracted_statement="ACT-1010 400m done.",
            raw_observed_activity_id="ACT-1010", observed_activity_id="ACT-1010",
            activity_id_validation_status="VALID_SCHEDULE_ID", temporal_resolution_status="EXPLICIT_DATE",
            discipline="CIVIL", observed_quantity=400.0,
            unit_of_measure="Meters", extraction_confidence=0.95, lifecycle_state=PipelineState.VALIDATED,
            provenance=prov
        )
        self.db.save_execution_event(event)

        events = self.db.get_events_by_source("SRC-1001")
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]["event_id"], "EVT-001")
        self.assertEqual(events[0]["raw_observed_activity_id"], "ACT-1010")
        self.assertEqual(events[0]["activity_id_validation_status"], "VALID_SCHEDULE_ID")

    def test_append_only_immutability(self):
        # Verify that event storage is strictly append-only (no UPDATE statements exist)
        with open("/Users/neemaysmac/Desktop/OIL_India_SIH/backend/persistence/database_engine.py") as f:
            code = f.read()
        self.assertNotIn("UPDATE execution_events", code)

if __name__ == "__main__":
    unittest.main()
