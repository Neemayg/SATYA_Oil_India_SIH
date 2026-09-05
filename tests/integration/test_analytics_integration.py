"""
SATYA Phase 14 Analytics & Institutional Memory Integration Test
Verifies complete end-to-end REST API lifecycle:
Ingestion -> Matching -> HITL Decision -> Memory Distillation -> REST Analytics API Queries.
"""

import os
import unittest
import json
from backend.persistence.database_engine import DatabaseEngine
from backend.api.app import SATYAApplicationAPI

class TestAnalyticsIntegration(unittest.TestCase):
    def setUp(self):
        self.db = DatabaseEngine(":memory:")
        self.api = SATYAApplicationAPI(self.db)

        # Seed baseline schedule fingerprint
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        schedule_path = os.path.join(base_dir, "data", "synthetic", "schedules", "baseline_schedule.json")
        status_fp, _, fp_res = self.api.dispatch(
            method="POST",
            path="/api/v1/fingerprints/index",
            body={
                "project_id": "PRJ-NBG-2026",
                "schedule_path": schedule_path
            }
        )
        self.assertEqual(status_fp, 200)

        vocab = self.api.fingerprint_service.get_valid_activity_vocabulary()
        self.api.pipeline_service.set_schedule_vocabulary(vocab)
        self.api.validation_service.set_valid_vocabulary(vocab)

    def test_end_to_end_analytics_lifecycle(self):
        # 1. Ingest DPR report with non-standard phrase
        dpr_text = "HDD trenchless drilling at Section 1 completed successfully."
        status_ing, _, ing_res = self.api.dispatch(
            method="POST",
            path="/api/v1/ingestion/upload",
            body={
                "project_id": "PRJ-NBG-2026",
                "source_type": "DPR",
                "file_name": "test_dpr.txt",
                "content": dpr_text
            }
        )
        self.assertEqual(status_ing, 201)
        event_id = ing_res["events_extracted"][0]["event_id"]

        # 2. Perform matching
        status_mth, _, mth_res = self.api.dispatch(
            method="POST",
            path="/api/v1/matching/match",
            body={"event_id": event_id}
        )
        self.assertEqual(status_mth, 200)

        # 3. Evaluate trust
        status_tru, _, tru_res = self.api.dispatch(
            method="POST",
            path="/api/v1/evidence/evaluate",
            body={"event_id": event_id}
        )
        self.assertEqual(status_tru, 200)

        # 4. Submit HITL CHANGE_MATCH decision to ACT-1010
        status_dec, _, dec_res = self.api.dispatch(
            method="POST",
            path="/api/v1/hitl/decisions",
            body={
                "event_id": event_id,
                "planner_id": "PLN-CHIEF-01",
                "decision_type": "CHANGE_MATCH",
                "reviewed_trust_version": self.api.db.get_latest_trust_assessment(event_id)["version_index"],
                "reviewed_match_result_id": mth_res["match_id"],
                "reviewed_evidence_assessment_id": tru_res.get("assessment_id", ""),
                "selected_activity_id": "ACT-1010",
                "override_reason_category": "TERMINOLOGY_ALIAS",
                "reason_notes": "HDD maps to ACT-1010"
            }
        )
        self.assertEqual(status_dec, 200)

        # 5. Trigger Memory Distillation via REST API
        status_dis, _, dis_res = self.api.dispatch(
            method="POST",
            path="/api/v1/memory/projects/PRJ-NBG-2026/distill",
            body={}
        )
        self.assertEqual(status_dis, 200)
        self.assertIn("distillation_run", dis_res)
        self.assertEqual(dis_res["distillation_run"]["candidates_created_count"], 1)

        # 6. Query Terminology Aliases via REST API
        status_ali, _, ali_res = self.api.dispatch(
            method="GET",
            path="/api/v1/memory/projects/PRJ-NBG-2026/aliases"
        )
        self.assertEqual(status_ali, 200)
        self.assertEqual(ali_res["total_count"], 1)
        self.assertEqual(ali_res["aliases"][0]["status"], "CANDIDATE")

        # 7. Query Productivity Analytics via REST API
        status_pro, _, pro_res = self.api.dispatch(
            method="GET",
            path="/api/v1/analytics/projects/PRJ-NBG-2026/productivity"
        )
        self.assertEqual(status_pro, 200)
        self.assertIn("benchmarks", pro_res)

        # 8. Query Contractor Scorecard via REST API
        status_con, _, con_res = self.api.dispatch(
            method="GET",
            path="/api/v1/analytics/projects/PRJ-NBG-2026/contractors"
        )
        self.assertEqual(status_con, 200)
        self.assertIn("disclaimer", con_res)

        # 9. Query Conflict Resolution Patterns via REST API
        status_pat, _, pat_res = self.api.dispatch(
            method="GET",
            path="/api/v1/analytics/projects/PRJ-NBG-2026/conflicts"
        )
        self.assertEqual(status_pat, 200)
        self.assertIn("patterns", pat_res)

if __name__ == "__main__":
    unittest.main()
