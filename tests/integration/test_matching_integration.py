import unittest
import os
from backend.persistence.database_engine import DatabaseEngine
from backend.services.fingerprint_service import ActivityFingerprintService
from backend.services.pipeline_service import ExecutionEventPipelineService
from backend.services.matching_service import ScheduleMatchingService
from backend.models.domain_models import SourceType, MatchOutcome

class TestMatchingIntegration(unittest.TestCase):
    def setUp(self):
        self.db = DatabaseEngine(":memory:")
        self.fp_service = ActivityFingerprintService(db_engine=self.db)
        self.pipeline_service = ExecutionEventPipelineService(db_engine=self.db)
        self.matching_service = ScheduleMatchingService(db_engine=self.db)

        self.base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.schedules_dir = os.path.join(self.base_dir, "data", "synthetic", "schedules")

        # Load baseline fingerprints
        self.fp_service.load_all_synthetic_schedules(self.schedules_dir)
        vocab = self.fp_service.get_valid_activity_vocabulary()
        self.pipeline_service.set_schedule_vocabulary(vocab)

    def test_end_to_end_pipeline_to_matching(self):
        raw = "ACT-1010: Mainline ROW Clearing & Grading Sec 1 completed 400m today."
        res = self.pipeline_service.process_source_payload(
            raw_content=raw,
            file_name="dpr.txt",
            project_id="PRJ-NBG-2026",
            source_type=SourceType.TEXT_DOCUMENT
        )
        self.assertEqual(len(res.events_extracted), 1)
        event = res.events_extracted[0]

        match_res = self.matching_service.match_event(event, project_id="PRJ-NBG-2026")
        self.assertEqual(match_res.outcome, MatchOutcome.MATCHED)
        self.assertEqual(match_res.selected_activity_id, "ACT-1010")
        self.assertGreaterEqual(match_res.confidence_score, 0.80)

        # Check DB persistence of MatchResult
        matches_in_db = self.db.get_match_results_by_event(event.event_id)
        self.assertEqual(len(matches_in_db), 1)
        self.assertEqual(matches_in_db[0]["selected_activity_id"], "ACT-1010")

    def test_unmatched_out_of_scope_field_observation(self):
        raw = "Constructed temporary timber bypass culvert near stream Ch 12+800 to facilitate crane movement."
        res = self.pipeline_service.process_source_payload(
            raw_content=raw,
            file_name="out_of_scope.txt",
            project_id="PRJ-NBG-2026",
            source_type=SourceType.TEXT_DOCUMENT
        )
        event = res.events_extracted[0]
        match_res = self.matching_service.match_event(event, project_id="PRJ-NBG-2026")
        self.assertEqual(match_res.outcome, MatchOutcome.UNMATCHED)
        self.assertIsNone(match_res.selected_activity_id)

if __name__ == "__main__":
    unittest.main()
