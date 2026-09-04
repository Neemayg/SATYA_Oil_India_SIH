import unittest
from backend.ingestion.source_ingestion import SourceIngestionService
from backend.models.domain_models import SourceType, PipelineState

class TestSourceIngestion(unittest.TestCase):
    def setUp(self):
        self.service = SourceIngestionService()

    def test_ingest_valid_source(self):
        content = "ACT-1010: Mainline ROW Clearing Sec 1 completed 400m today."
        doc, is_dup = self.service.ingest_raw_source(
            raw_content=content,
            file_name="test_dpr.txt",
            project_id="PRJ-NBG-2026",
            source_type=SourceType.TEXT_DOCUMENT,
            author="Tester"
        )
        self.assertFalse(is_dup)
        self.assertIsNotNone(doc.source_id)
        self.assertEqual(doc.extraction_status, PipelineState.INGESTED)
        self.assertEqual(len(doc.sha256_hash), 64)

    def test_idempotency_duplicate_ingestion(self):
        content = "ACT-1010: Mainline ROW Clearing Sec 1 completed 400m today."
        doc1, is_dup1 = self.service.ingest_raw_source(
            raw_content=content, file_name="test_dpr.txt", project_id="PRJ-NBG-2026"
        )
        doc2, is_dup2 = self.service.ingest_raw_source(
            raw_content=content, file_name="test_dpr.txt", project_id="PRJ-NBG-2026"
        )
        self.assertFalse(is_dup1)
        self.assertTrue(is_dup2)
        self.assertEqual(doc1.source_id, doc2.source_id)

    def test_empty_content_raises_error(self):
        with self.assertRaises(ValueError):
            self.service.ingest_raw_source(raw_content="", file_name="empty.txt", project_id="PRJ-NBG-2026")

    def test_xlsx_adapter_instantiation(self):
        from backend.ingestion.xlsx_adapter import XLSXAdapter
        adapter = XLSXAdapter()
        records = adapter.parse_xlsx_bytes(b"dummy_bytes")
        self.setIsInstance = True
        self.assertEqual(records, [])

if __name__ == "__main__":
    unittest.main()
