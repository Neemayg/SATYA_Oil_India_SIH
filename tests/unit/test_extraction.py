import unittest
from backend.extraction.event_extractor import ExecutionEventExtractionService
from backend.models.domain_models import SourceDocument, SourceFragment, EventType, SourceType

class TestEventExtraction(unittest.TestCase):
    def setUp(self):
        self.service = ExecutionEventExtractionService()

    def test_extract_quantities_and_uom(self):
        text = "Completed 180m trenching at Ch 14+100."
        qty, uom = self.service.extract_quantity_and_uom(text)
        self.assertEqual(qty, 180.0)
        self.assertEqual(uom, "Meters")

    def test_extract_real_world_fields(self):
        text = "U3 24in line erection taken up in night shift, balance 2 joints pending; clearance awaited from QA."
        shift, pending_qa, rem_qty, work_front = self.service.extract_real_world_fields(text)
        self.assertEqual(shift, "NIGHT_SHIFT")
        self.assertTrue(pending_qa)
        self.assertEqual(rem_qty, 2.0)

    def test_extract_event_from_fragment(self):
        doc = SourceDocument(
            source_id="SRC-101", project_id="PRJ-NBG-2026", source_type=SourceType.DPR_EXCEL,
            file_name="dpr.xlsx", sha256_hash="hash123", raw_content="ACT-1010: Mainline ROW Clearing 400m done.",
            submitted_at="2026-09-02T10:00:00Z", received_at="2026-09-02T10:00:00Z"
        )
        frag = SourceFragment(
            fragment_id="FRG-001", source_id=doc.source_id, fragment_index=0,
            raw_text="ACT-1010: Mainline ROW Clearing 400m done.",
            normalized_text="ACT-1010: Mainline ROW Clearing 400m done.",
            locator_type="EXCEL_CELL", locator_value="Sheet1!R12"
        )
        event = self.service.extract_event_from_fragment(doc, frag)
        self.assertEqual(event.raw_observed_activity_id, "ACT-1010")
        self.assertEqual(event.discipline, "CIVIL")
        self.assertEqual(event.observed_quantity, 400.0)
        self.assertEqual(event.provenance.locator_value, "Sheet1!R12")

    def test_compound_fragment_decomposition_one_to_many(self):
        doc = SourceDocument(
            source_id="SRC-102", project_id="PRJ-NBG-2026", source_type=SourceType.TEXT_DOCUMENT,
            file_name="compound.txt", sha256_hash="hash456",
            raw_content="Piping crew completed erection of Line 24-XX from CH 12+400 to 12+650 and started valve installation at V-204; QA clearance pending.",
            submitted_at="2026-09-02T10:00:00Z", received_at="2026-09-02T10:00:00Z"
        )
        frag = SourceFragment(
            fragment_id="FRG-002", source_id=doc.source_id, fragment_index=0,
            raw_text=doc.raw_content, normalized_text=doc.raw_content,
            locator_type="TEXT_LINE", locator_value="Line 1"
        )
        events = self.service.extract_events_from_fragment(doc, frag)
        # Should decompose into 3 distinct events: FINISH erection, START valve installation, QA_CLEARANCE/HOLD
        self.assertEqual(len(events), 3)
        self.assertEqual(events[0].event_type, EventType.FINISH)
        self.assertEqual(events[1].event_type, EventType.START)
        self.assertTrue(events[2].pending_qa_clearance)

    def test_field_level_provenance_spans(self):
        doc = SourceDocument(
            source_id="SRC-103", project_id="PRJ-NBG-2026", source_type=SourceType.TEXT_DOCUMENT,
            file_name="prov.txt", sha256_hash="hash789", raw_content="ACT-1010: Completed 180m trenching at Section 1.",
            submitted_at="2026-09-02T10:00:00Z", received_at="2026-09-02T10:00:00Z"
        )
        frag = SourceFragment(
            fragment_id="FRG-003", source_id=doc.source_id, fragment_index=0,
            raw_text=doc.raw_content, normalized_text=doc.raw_content,
            locator_type="TEXT_LINE", locator_value="Line 1"
        )
        event = self.service.extract_event_from_fragment(doc, frag)
        prov_map = event.provenance.field_provenance_map
        self.assertIn("observed_quantity", prov_map)
        self.assertEqual(prov_map["observed_quantity"]["snippet"], "180m")
        self.assertIn("raw_observed_activity_id", prov_map)
        self.assertEqual(prov_map["raw_observed_activity_id"]["snippet"], "ACT-1010")

if __name__ == "__main__":
    unittest.main()
