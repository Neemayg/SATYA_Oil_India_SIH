import unittest
from backend.normalization.content_normalization import ContentNormalizationService
from backend.models.domain_models import SourceDocument, SourceType

class TestContentNormalization(unittest.TestCase):
    def setUp(self):
        self.service = ContentNormalizationService()

    def test_normalize_whitespace(self):
        raw = "  ACT-1010:   Mainline   Trenching\r\n  Line 2   "
        clean = self.service.normalize_text(raw)
        self.assertEqual(clean, "ACT-1010: Mainline Trenching\n Line 2")

    def test_resolve_relative_date_yesterday(self):
        text = "Shift 2 yesterday completed alignment of Vessel V-101."
        ref_date = "2026-09-06"
        res_date, status, reason = self.service.resolve_relative_date(text, ref_date)
        self.assertEqual(res_date, "2026-09-05")
        self.assertEqual(status, "RESOLVED_RELATIVE_DATE")

    def test_resolve_relative_date_unresolved_when_missing_reference(self):
        text = "Yesterday excavation completed."
        res_date, status, reason = self.service.resolve_relative_date(text, None)
        self.assertIsNone(res_date)
        self.assertEqual(status, "UNRESOLVED_RELATIVE_DATE")

    def test_fragmentation_multi_line_text(self):
        doc = SourceDocument(
            source_id="SRC-101", project_id="PRJ-NBG-2026", source_type=SourceType.TEXT_DOCUMENT,
            file_name="site_log.txt", sha256_hash="hash123", raw_content="Line 1 Work Done\nLine 2 More Work",
            submitted_at="2026-09-02T10:00:00Z", received_at="2026-09-02T10:00:00Z"
        )
        fragments = self.service.fragment_document(doc)
        self.assertEqual(len(fragments), 2)
        self.assertEqual(fragments[0].locator_type, "TEXT_LINE")
        self.assertEqual(fragments[0].locator_value, "Line 1")

if __name__ == "__main__":
    unittest.main()
