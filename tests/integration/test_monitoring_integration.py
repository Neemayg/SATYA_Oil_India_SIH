"""
SATYA REST API Monitoring Integration Tests (Phase 13)
Verifies end-to-end flow: Ingestion -> Projection -> REST Time Agent Evaluation -> Signal Persistence -> Deduplication -> Retrieval.
"""

import os
import unittest
from backend.persistence.database_engine import DatabaseEngine
from backend.api.app import SATYAApplicationAPI
from backend.models.domain_models import SignalStatus, TemporalSignalType

class TestMonitoringIntegration(unittest.TestCase):

    def setUp(self):
        self.db = DatabaseEngine(":memory:")
        self.api = SATYAApplicationAPI(self.db)
        self.project_id = "PRJ-NBG-2026"

        # Index baseline schedule
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        schedule_path = os.path.join(base_dir, "data", "synthetic", "schedules", "baseline_schedule.json")
        self.api.fingerprint_service.process_schedule_file(schedule_path)

        vocab = self.api.fingerprint_service.get_valid_activity_vocabulary()
        self.api.pipeline_service.set_schedule_vocabulary(vocab)
        self.api.validation_service.set_valid_vocabulary(vocab)

    def test_end_to_end_monitoring_evaluation_via_rest_api(self):
        # 1. Ingest DPR for ACT-1010
        code1, _, body1 = self.api.dispatch("POST", "/api/v1/ingestion/upload", body={
            "project_id": self.project_id,
            "source_type": "DPR_EXCEL",
            "file_name": "dpr_mon.txt",
            "content": "2026-09-02: Mainline trench excavation 350m completed on PL-NBG-SEC1 ACT-1010. QA cleared."
        })
        self.assertEqual(code1, 201)
        event_id = body1["events_extracted"][0]["event_id"]

        # 2. Run Matching, Trust, and Projection
        self.api.dispatch("POST", "/api/v1/matching/match", body={"event_id": event_id})
        self.api.dispatch("POST", "/api/v1/evidence/evaluate", body={"event_id": event_id})
        self.api.dispatch("POST", "/api/v1/projections/generate", body={
            "project_id": self.project_id,
            "as_of_date": "2026-09-05"
        })

        # 3. Execute Time Agent Evaluation via REST API
        code_eval, _, body_eval = self.api.dispatch("POST", "/api/v1/monitoring/evaluate", body={
            "project_id": self.project_id,
            "as_of_date": "2026-09-05"
        })
        self.assertEqual(code_eval, 200)
        self.assertIn("evaluation_run", body_eval)
        self.assertIn("signals", body_eval)

        run_info = body_eval["evaluation_run"]
        self.assertEqual(run_info["project_id"], self.project_id)
        self.assertGreaterEqual(run_info["total_signals_detected"], 0)

        # 4. Query Active Signals via REST API
        code_sig, _, body_sig = self.api.dispatch("GET", f"/api/v1/monitoring/projects/{self.project_id}/signals")
        self.assertEqual(code_sig, 200)
        self.assertEqual(body_sig["project_id"], self.project_id)
        self.assertIn("signals", body_sig)

        # 5. Deduplication & Idempotency Check: Run evaluation a second time
        code_eval2, _, body_eval2 = self.api.dispatch("POST", "/api/v1/monitoring/evaluate", body={
            "project_id": self.project_id,
            "as_of_date": "2026-09-05"
        })
        self.assertEqual(code_eval2, 200)

        # Confirm active signals count is repeat-safe and deduplicated
        code_sig2, _, body_sig2 = self.api.dispatch("GET", f"/api/v1/monitoring/projects/{self.project_id}/signals")
        self.assertEqual(code_sig2, 200)
        self.assertEqual(len(body_sig2["signals"]), len(body_sig["signals"]))

if __name__ == "__main__":
    unittest.main()
