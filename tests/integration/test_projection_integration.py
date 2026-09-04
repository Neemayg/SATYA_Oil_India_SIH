"""
SATYA Schedule Projection Engine Integration Test (Phase 10)
Verifies end-to-end flow from raw ingestion -> matching -> trust evaluation ->
planner HITL validation -> trusted execution truth -> schedule projection generation,
while strictly verifying baseline schedule immutability.
"""

import os
import json
import hashlib
import unittest

from backend.persistence.database_engine import DatabaseEngine
from backend.services.pipeline_service import ExecutionEventPipelineService
from backend.services.fingerprint_service import ActivityFingerprintService
from backend.services.matching_service import ScheduleMatchingService
from backend.services.trust_evaluator_service import TrustEvaluatorService
from backend.hitl.validation_service import ValidationService
from backend.projection.projection_service import ScheduleProjectionService
from backend.models.domain_models import OverrideReasonCategory, TrustStatus, ActivityProgressStatus

class TestScheduleProjectionIntegration(unittest.TestCase):

    def setUp(self):
        self.db = DatabaseEngine(":memory:")
        self.pipeline_service = ExecutionEventPipelineService(self.db)
        self.fingerprint_service = ActivityFingerprintService(self.db)
        self.matching_service = ScheduleMatchingService(self.db)
        self.trust_service = TrustEvaluatorService(self.db)
        self.validation_service = ValidationService(self.db)
        self.projection_service = ScheduleProjectionService(self.db)

        # Index test baseline schedule
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.schedule_path = os.path.join(base_dir, "data", "synthetic", "schedules", "baseline_schedule.json")
        self.fingerprint_service.process_schedule_file(self.schedule_path)

        # Set schedule vocabulary for Rule 5 guardrails
        vocab = self.fingerprint_service.get_valid_activity_vocabulary()
        self.pipeline_service.set_schedule_vocabulary(vocab)
        self.validation_service.set_valid_vocabulary(vocab)

    def test_end_to_end_schedule_projection_pipeline(self):
        # Hash baseline schedule file before processing
        with open(self.schedule_path, "rb") as f:
            hash_before = hashlib.sha256(f.read()).hexdigest()

        # 1. Ingest raw DPR
        dpr_content = "2026-09-02: Mainline trench excavation 500m completed on PL-NBG-SEC1 ACT-1011. QA cleared."
        run_res = self.pipeline_service.process_source_payload(
            raw_content=dpr_content,
            project_id="PRJ-NBG-2026",
            source_type="DPR_EXCEL",
            file_name="dpr_excavation_sec1.txt"
        )
        self.assertGreaterEqual(len(run_res.events_extracted), 1)
        event = run_res.events_extracted[0]

        # 2. Schedule Matching (Phase 7)
        match_res = self.matching_service.match_event(event)
        self.assertIsNotNone(match_res)

        # 3. Trust Assessment (Phase 8)
        trust_res = self.trust_service.evaluate_trust_for_event(event, match_res)
        self.assertIsNotNone(trust_res)

        # 4. Planner HITL Validation (Phase 9) -> Validate match to ACT-1011
        decision = self.validation_service.validate_event(
            event_id=event.event_id,
            planner_id="PLN-CHIEF-01",
            reason_notes="Verified trench excavation 500m under ACT-1011."
        )
        self.assertEqual(decision.resulting_trust_status, TrustStatus.TRUSTED)

        # 5. Schedule Projection Generation (Phase 10)
        projection = self.projection_service.generate_projection_for_project(
            project_id="PRJ-NBG-2026",
            as_of_date="2026-09-05",
            schedule_json_path=self.schedule_path
        )

        self.assertIsNotNone(projection)
        self.assertEqual(projection.project_id, "PRJ-NBG-2026")
        self.assertGreater(projection.total_activities, 0)
        self.assertGreaterEqual(projection.in_progress_activities + projection.completed_activities, 1)
        self.assertGreater(projection.overall_project_progress_pct, 0.0)

        # Verify activity progress state
        act_prog = projection.activity_progress_map.get("ACT-1011")
        self.assertIsNotNone(act_prog)
        self.assertEqual(act_prog.physical_progress_pct, 25.0)  # 500m / 2000m planned = 25%
        self.assertEqual(act_prog.status, ActivityProgressStatus.IN_PROGRESS)

        # 6. Verify SQLite Database persistence
        latest_saved = self.db.get_latest_schedule_projection("PRJ-NBG-2026")
        self.assertIsNotNone(latest_saved)
        self.assertEqual(latest_saved["projection_id"], projection.projection_id)

        # 7. Baseline File Immutability Verification
        with open(self.schedule_path, "rb") as f:
            hash_after = hashlib.sha256(f.read()).hexdigest()
        self.assertEqual(hash_before, hash_after)

if __name__ == "__main__":
    unittest.main()
