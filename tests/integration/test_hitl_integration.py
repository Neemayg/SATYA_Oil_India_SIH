"""
SATYA Human Validation (HITL) Integration Test (Phase 9)
Verifies end-to-end integration across raw ingestion, extraction, fingerprinting,
matching, trust evaluation, queue placement, planner re-mapping decision (CHANGE_MATCH),
and append-only trusted execution truth persistence.
"""

import os
import unittest
from backend.persistence.database_engine import DatabaseEngine
from backend.services.pipeline_service import ExecutionEventPipelineService
from backend.services.fingerprint_service import ActivityFingerprintService
from backend.services.matching_service import ScheduleMatchingService
from backend.services.trust_evaluator_service import TrustEvaluatorService
from backend.hitl.queue_manager import PlannerQueueManager
from backend.hitl.validation_service import ValidationService
from backend.models.domain_models import TrustStatus, ValidationDecisionType, OverrideReasonCategory

class TestHITLIntegration(unittest.TestCase):

    def setUp(self):
        self.db = DatabaseEngine(":memory:")
        self.pipeline_service = ExecutionEventPipelineService(self.db)
        self.fingerprint_service = ActivityFingerprintService(self.db)
        self.matching_service = ScheduleMatchingService(self.db)
        self.trust_service = TrustEvaluatorService(self.db)
        self.queue_manager = PlannerQueueManager(self.db)
        self.validation_service = ValidationService(self.db)

        # Index test baseline schedule
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        schedule_path = os.path.join(base_dir, "data", "synthetic", "schedules", "baseline_schedule.json")
        self.fingerprint_service.process_schedule_file(schedule_path)

        # Set schedule vocabulary for Rule 5 guardrails
        vocab = self.fingerprint_service.get_valid_activity_vocabulary()
        self.pipeline_service.set_schedule_vocabulary(vocab)
        self.validation_service.set_valid_vocabulary(vocab)

    def test_end_to_end_hitl_planner_override_workflow(self):
        # 1. Ingest raw DPR
        dpr_content = "2026-09-02: Mainline trench excavation 350m completed on PL-NBG-SEC1 ACT-1010. QA pending."
        run_res = self.pipeline_service.process_source_payload(
            raw_content=dpr_content,
            project_id="PRJ-NBG-2026",
            source_type="DPR_EXCEL",
            file_name="dpr_excavation.txt"
        )
        self.assertGreaterEqual(len(run_res.events_extracted), 1)
        event = run_res.events_extracted[0]

        # 2. Schedule Matching (Phase 7)
        match_res = self.matching_service.match_event(event)
        self.assertIsNotNone(match_res)

        # 3. Trust Assessment (Phase 8) -> Initial state REVIEW_REQUIRED due to pending QA
        trust_res = self.trust_service.evaluate_trust_for_event(event, match_res)
        self.assertIsNotNone(trust_res)

        # 4. Query Review Queue (Phase 9)
        queue_items = self.queue_manager.get_review_queue(project_id="PRJ-NBG-2026")
        self.assertGreaterEqual(len(queue_items), 1)

        # 5. Planner Review Decision: CHANGE_MATCH to ACT-1020
        decision = self.validation_service.change_match(
            event_id=event.event_id,
            new_activity_id="ACT-1020",
            planner_id="PLN-CHIEF-01",
            reason_category=OverrideReasonCategory.SPATIAL_CHAINAGE_RECURRENCE,
            reason_notes="Re-mapped to Section 2 Trench Excavation ACT-1020 based on chainage survey."
        )

        self.assertEqual(decision.decision_type, ValidationDecisionType.CHANGE_MATCH)
        self.assertEqual(decision.selected_activity_id, "ACT-1020")
        self.assertEqual(decision.resulting_trust_status, TrustStatus.TRUSTED)

        # 6. Verify Original MatchResult was NOT mutated
        original_matches = self.db.get_match_results_by_event(event.event_id)
        self.assertEqual(len(original_matches), 1)

        # 7. Verify Trust History Ledger contains version 1 (REVIEW_REQUIRED) and version 2 (TRUSTED)
        trust_history = self.db.get_trust_assessments_by_event(event.event_id)
        self.assertEqual(len(trust_history), 2)
        self.assertEqual(trust_history[0]["trust_status"], trust_res.trust_status)
        self.assertEqual(trust_history[1]["trust_status"], TrustStatus.TRUSTED)

        # 8. Verify Derived PlannerCorrectionRecord stored for Phase 14 Institutional Memory
        corrections = self.db.get_planner_corrections()
        self.assertEqual(len(corrections), 1)
        self.assertEqual(corrections[0]["corrected_activity_id"], "ACT-1020")

if __name__ == "__main__":
    unittest.main()
