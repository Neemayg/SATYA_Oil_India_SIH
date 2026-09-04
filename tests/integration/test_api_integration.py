"""
SATYA Backend Application API End-to-End Integration Test (Phase 11)
Executes full execution intelligence pipeline (Ingestion -> Fingerprinting -> Matching -> Trust -> HITL -> Projection)
via REST API endpoints.
"""

import os
import json
import unittest
from backend.persistence.database_engine import DatabaseEngine
from backend.api.app import SATYAApplicationAPI
from backend.models.domain_models import ValidationDecisionType, TrustStatus, ActivityProgressStatus

class TestAPIIntegration(unittest.TestCase):

    def setUp(self):
        self.db = DatabaseEngine(":memory:")
        self.api = SATYAApplicationAPI(self.db)
        self.project_id = "PRJ-NBG-2026"

        # Index baseline schedule
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.schedule_path = os.path.join(base_dir, "data", "synthetic", "schedules", "baseline_schedule.json")
        self.api.fingerprint_service.process_schedule_file(self.schedule_path)

        # Set schedule vocabulary for Rule 5 guardrails
        vocab = self.api.fingerprint_service.get_valid_activity_vocabulary()
        self.api.pipeline_service.set_schedule_vocabulary(vocab)
        self.api.validation_service.set_valid_vocabulary(vocab)

    def test_full_pipeline_via_rest_api(self):
        # 1. Ingest DPR via API
        dpr_content = "2026-09-02: Mainline trench excavation 500m completed on PL-NBG-SEC1 ACT-1011. QA cleared."
        code1, _, body1 = self.api.dispatch("POST", "/api/v1/ingestion/upload", body={
            "project_id": self.project_id,
            "source_type": "DPR_EXCEL",
            "file_name": "dpr_api_test.txt",
            "content": dpr_content
        })
        self.assertEqual(code1, 201)
        event_id = body1["events_extracted"][0]["event_id"]

        # 2. Schedule Matching via API
        code2, _, body2 = self.api.dispatch("POST", "/api/v1/matching/match", body={"event_id": event_id})
        self.assertEqual(code2, 200)
        self.assertEqual(body2["selected_activity_id"], "ACT-1011")

        # 3. Trust Evaluation via API
        code3, _, body3 = self.api.dispatch("POST", "/api/v1/evidence/evaluate", body={"event_id": event_id})
        self.assertEqual(code3, 200)

        # 4. Fetch Review Queue via API
        code4, _, body4 = self.api.dispatch("GET", "/api/v1/hitl/queue", params={"project_id": self.project_id})
        self.assertEqual(code4, 200)

        # 5. Submit Planner Decision via API (VALIDATE)
        code5, _, body5 = self.api.dispatch("POST", "/api/v1/hitl/decisions", body={
            "event_id": event_id,
            "planner_id": "PLN-CHIEF-01",
            "decision_type": ValidationDecisionType.VALIDATE,
            "reviewed_trust_version": 1,
            "reviewed_match_result_id": body2["match_id"],
            "reviewed_evidence_assessment_id": "EVA-1",
            "reason_notes": "Validated via API."
        })
        self.assertEqual(code5, 200)
        self.assertEqual(body5["resulting_trust_status"], TrustStatus.TRUSTED)

        # 6. Generate Schedule Projection via API
        code6, _, body6 = self.api.dispatch("POST", "/api/v1/projections/generate", body={
            "project_id": self.project_id,
            "as_of_date": "2026-09-05"
        })
        self.assertEqual(code6, 200)
        self.assertGreater(body6["overall_project_progress_pct"], 0.0)

        # 7. Fetch Activity Progress Details via API
        code7, _, body7 = self.api.dispatch("GET", f"/api/v1/projections/projects/{self.project_id}/activities/ACT-1011")
        self.assertEqual(code7, 200)
        act_prog = body7["activity_progress"]
        self.assertEqual(act_prog["physical_progress_pct"], 25.0)
        self.assertEqual(act_prog["status"], ActivityProgressStatus.IN_PROGRESS)

if __name__ == "__main__":
    unittest.main()
