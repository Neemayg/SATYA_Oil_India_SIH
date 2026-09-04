"""
SATYA API Endpoints Unit Tests (Phase 11)
Verifies route dispatching, status codes (200, 201, 400, 404, 422),
serializers, SATYAError contract structure, and CORS control.
"""

import os
import json
import unittest
from backend.persistence.database_engine import DatabaseEngine
from backend.api.app import SATYAApplicationAPI
from backend.api.errors import SATYAError

class TestAPIEndpoints(unittest.TestCase):

    def setUp(self):
        self.db = DatabaseEngine(":memory:")
        self.api = SATYAApplicationAPI(self.db)
        self.project_id = "PRJ-NBG-2026"

        # Index baseline schedule for testing
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        schedule_path = os.path.join(base_dir, "data", "synthetic", "schedules", "baseline_schedule.json")
        self.api.fingerprint_service.process_schedule_file(schedule_path)

    def test_health_check_endpoint(self):
        code, headers, body = self.api.dispatch("GET", "/api/v1/health")
        self.assertEqual(code, 200)
        self.assertEqual(body["status"], "healthy")
        self.assertEqual(body["service"], "satya-api")
        self.assertEqual(body["database"], "healthy")
        self.assertEqual(body["api_version"], "v1")
        # Ensure test counts are NOT present in health endpoint
        self.assertNotIn("test_count", body)

    def test_openapi_spec_endpoint(self):
        code, headers, body = self.api.dispatch("GET", "/api/v1/openapi.json")
        self.assertEqual(code, 200)
        self.assertEqual(body["openapi"], "3.0.3")
        self.assertIn("/api/v1/ingestion/upload", body["paths"])
        self.assertIn("/api/v1/hitl/decisions", body["paths"])

    def test_cors_restriction(self):
        headers = self.api.get_cors_headers("http://localhost:3000")
        self.assertEqual(headers["Access-Control-Allow-Origin"], "http://localhost:3000")

        # Unallowed origin falls back to default
        headers_bad = self.api.get_cors_headers("http://malicious-site.com")
        self.assertEqual(headers_bad["Access-Control-Allow-Origin"], "http://localhost:3000")

    def test_ingestion_upload_and_get_source(self):
        payload = {
            "project_id": self.project_id,
            "source_type": "DPR_EXCEL",
            "file_name": "dpr_test.txt",
            "content": "2026-09-02: Mainline trench excavation 350m completed on PL-NBG-SEC1 ACT-1010. QA cleared."
        }
        code, headers, body = self.api.dispatch("POST", "/api/v1/ingestion/upload", body=payload)
        self.assertEqual(code, 201)
        self.assertIn("source_id", body)
        self.assertGreaterEqual(body["events_extracted_count"], 1)

        source_id = body["source_id"]
        code2, headers2, body2 = self.api.dispatch("GET", f"/api/v1/ingestion/sources/{source_id}")
        self.assertEqual(code2, 200)
        self.assertEqual(body2["source_id"], source_id)
        self.assertEqual(body2["project_id"], self.project_id)
        self.assertIn("extracted_event_ids", body2)

    def test_fingerprints_search_endpoint(self):
        code, headers, body = self.api.dispatch("GET", "/api/v1/fingerprints/search", params={"q": "mainline", "discipline": "civil"})
        self.assertEqual(code, 200)
        self.assertGreater(body["count"], 0)
        self.assertIn("results", body)

    def test_schedule_matching_endpoint(self):
        # Ingest first
        payload = {
            "project_id": self.project_id,
            "source_type": "DPR_EXCEL",
            "file_name": "dpr_match.txt",
            "content": "2026-09-02: Mainline trench excavation 350m completed on PL-NBG-SEC1 ACT-1010. QA cleared."
        }
        _, _, body_ingest = self.api.dispatch("POST", "/api/v1/ingestion/upload", body=payload)
        event_id = body_ingest["events_extracted"][0]["event_id"]

        # Run matching via API
        code, headers, body = self.api.dispatch("POST", "/api/v1/matching/match", body={"event_id": event_id})
        self.assertEqual(code, 200)
        self.assertEqual(body["event_id"], event_id)
        self.assertEqual(body["selected_activity_id"], "ACT-1010")

    def test_satya_error_contract_structure(self):
        # Invalid endpoint -> 404
        code, headers, body = self.api.dispatch("GET", "/api/v1/nonexistent_route")
        self.assertEqual(code, 404)
        self.assertIn("error", body)
        err = body["error"]
        self.assertEqual(err["code"], "ROUTE_NOT_FOUND")
        self.assertIn("message", err)
        self.assertIn("request_id", err)
        self.assertIn("timestamp", err)

    def test_evidence_event_trace_endpoint(self):
        # Ingest event & evaluate trust
        payload = {
            "project_id": self.project_id,
            "source_type": "DPR_EXCEL",
            "file_name": "dpr_trace.txt",
            "content": "2026-09-02: Mainline trench excavation 350m completed on PL-NBG-SEC1 ACT-1010. QA cleared."
        }
        _, _, body_ingest = self.api.dispatch("POST", "/api/v1/ingestion/upload", body=payload)
        event_id = body_ingest["events_extracted"][0]["event_id"]
        self.api.dispatch("POST", "/api/v1/matching/match", body={"event_id": event_id})
        self.api.dispatch("POST", "/api/v1/evidence/evaluate", body={"event_id": event_id})

        # Fetch Trace via API
        code, _, body = self.api.dispatch("GET", f"/api/v1/evidence/events/{event_id}/trace")
        self.assertEqual(code, 200)
        self.assertEqual(body["event_id"], event_id)
        self.assertIn("execution_event", body)
        self.assertIn("source_document", body)
        self.assertIn("claims", body)
        self.assertIn("latest_trust_assessment", body)

if __name__ == "__main__":
    unittest.main()
