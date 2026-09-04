"""
SATYA Evidence, Confidence & Conflict Engine Integration Test (Phase 8)
Verifies vertical integration across raw ingestion, extraction, fingerprinting,
matching, claim extraction, corroboration, gap/conflict detection, and trust assessment persistence.
"""

import os
import unittest
from backend.persistence.database_engine import DatabaseEngine
from backend.services.pipeline_service import ExecutionEventPipelineService
from backend.services.fingerprint_service import ActivityFingerprintService
from backend.services.matching_service import ScheduleMatchingService
from backend.services.trust_evaluator_service import TrustEvaluatorService
from backend.models.domain_models import TrustStatus, SourceDocument, SourceFragment

class TestEvidenceTrustIntegration(unittest.TestCase):

    def setUp(self):
        self.db = DatabaseEngine(":memory:")
        self.pipeline_service = ExecutionEventPipelineService(self.db)
        self.fingerprint_service = ActivityFingerprintService(self.db)
        self.matching_service = ScheduleMatchingService(self.db)
        self.trust_service = TrustEvaluatorService(self.db)

        # Index test baseline schedule
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        schedule_path = os.path.join(base_dir, "data", "synthetic", "schedules", "baseline_schedule.json")
        self.fingerprint_service.process_schedule_file(schedule_path)

    def test_end_to_end_evidence_trust_pipeline(self):
        # 1. Ingest raw DPR
        dpr_content = "2026-09-02: Mainline ROW clearing 400m completed on PL-16-01 under ACT-1010. QA cleared."
        run_res = self.pipeline_service.process_source_payload(
            raw_content=dpr_content,
            project_id="PRJ-NBG-2026",
            source_type="DPR_EXCEL",
            file_name="dpr_test.txt"
        )
        self.assertGreaterEqual(len(run_res.events_extracted), 1)
        event = run_res.events_extracted[0]

        # 2. Schedule Matching (Phase 7)
        match_res = self.matching_service.match_event(event)
        self.assertIsNotNone(match_res)

        # 3. Fetch Source Doc & Fragment
        source_doc_dict = self.db.get_events_by_source(event.source_id)
        self.assertTrue(len(source_doc_dict) > 0)

        source_doc = SourceDocument(
            source_id=event.source_id,
            project_id="PRJ-NBG-2026",
            source_type="DPR_EXCEL",
            file_name="dpr_test.txt",
            sha256_hash="hash123",
            raw_content=dpr_content,
            submitted_at="2026-09-02",
            received_at="2026-09-02",
            author="Site Supervisor"
        )
        source_frag = SourceFragment(
            fragment_id=event.fragment_id,
            source_id=event.source_id,
            fragment_index=0,
            raw_text=dpr_content,
            normalized_text=dpr_content,
            locator_type="TEXT_SPAN",
            locator_value="Line 1"
        )

        # 4. Evaluate Trust Assessment (Phase 8)
        trust_res = self.trust_service.evaluate_trust_for_event(
            event=event,
            match_result=match_res,
            source_doc=source_doc,
            source_fragment=source_frag
        )

        self.assertIsNotNone(trust_res)
        self.assertEqual(trust_res.version_index, 1)
        self.assertEqual(trust_res.trust_status, TrustStatus.TRUSTED)

        # 5. Query persisted trust assessment from SQLite database
        persisted_ta = self.db.get_latest_trust_assessment(event.event_id)
        self.assertIsNotNone(persisted_ta)
        self.assertEqual(persisted_ta["trust_status"], TrustStatus.TRUSTED)
        self.assertEqual(persisted_ta["version_index"], 1)

if __name__ == "__main__":
    unittest.main()
