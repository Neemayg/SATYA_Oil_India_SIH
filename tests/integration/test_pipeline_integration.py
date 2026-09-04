import unittest
import os
import json
from backend.services.pipeline_service import ExecutionEventPipelineService
from backend.models.domain_models import PipelineState, SourceType

class TestPipelineIntegration(unittest.TestCase):
    def setUp(self):
        self.vocab = {"ACT-1010", "ACT-1011", "ACT-1012", "ACT-4020", "ACT-SCP-8010"}
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        sched_dir = os.path.join(base_dir, "data", "synthetic", "schedules")
        for sfile in ["baseline_schedule.json", "project2_baseline_schedule.json"]:
            spath = os.path.join(sched_dir, sfile)
            if os.path.exists(spath):
                with open(spath) as f:
                    data = json.load(f)
                    activities = data.get("activities", []) if isinstance(data, dict) else data
                    for act in activities:
                        if isinstance(act, dict) and "activity_id" in act:
                            self.vocab.add(act["activity_id"])
        self.service = ExecutionEventPipelineService(valid_vocab=self.vocab)

    def test_full_pipeline_valid_source_with_activity_id(self):
        raw = "ACT-1010: Mainline ROW Clearing & Grading Sec 1 completed 400m today."
        result = self.service.process_source_payload(
            raw_content=raw,
            file_name="test_dpr.txt",
            project_id="PRJ-NBG-2026",
            source_type=SourceType.TEXT_DOCUMENT,
            author="J. Dutta",
            submitted_at="2026-09-02T10:00:00Z"
        )
        self.assertEqual(result.status, "SUCCESS")
        self.assertEqual(len(result.events_extracted), 1)
        
        event = result.events_extracted[0]
        self.assertEqual(event.observed_activity_id, "ACT-1010")
        self.assertEqual(event.observed_quantity, 400.0)
        self.assertEqual(event.unit_of_measure, "Meters")
        self.assertEqual(event.discipline, "CIVIL")
        self.assertEqual(event.lifecycle_state, PipelineState.VALIDATED)
        self.assertIsNotNone(event.provenance)
        self.assertEqual(event.provenance.raw_text_snippet, raw)

    def test_pipeline_missing_activity_id_does_not_fabricate(self):
        raw = "Trench excavation in progress Section 1 with 350m dug."
        result = self.service.process_source_payload(
            raw_content=raw,
            file_name="test_log.txt",
            project_id="PRJ-NBG-2026",
            source_type=SourceType.SITE_DIARY
        )
        self.assertEqual(result.status, "SUCCESS")
        event = result.events_extracted[0]
        # CRITICAL RULE 5: Activity ID must NOT be fabricated!
        self.assertIsNone(event.observed_activity_id)
        self.assertEqual(event.observed_quantity, 350.0)
        self.assertEqual(event.discipline, "CIVIL")

    def test_pipeline_invalid_activity_id_resets_and_warns(self):
        raw = "ACT-9999: Unknown activity task 100m done."
        result = self.service.process_source_payload(
            raw_content=raw,
            file_name="test_invalid.txt",
            project_id="PRJ-NBG-2026"
        )
        self.assertEqual(result.status, "SUCCESS")
        event = result.events_extracted[0]
        # Guardrail resets invalid Activity ID to None
        self.assertIsNone(event.observed_activity_id)
        # CRITICAL SAFEGUARD: Raw text ID is preserved!
        self.assertEqual(event.raw_observed_activity_id, "ACT-9999")
        self.assertEqual(event.activity_id_validation_status, "INVALID_EXPLICIT_REFERENCE")
        self.assertEqual(len(result.quarantine_records), 1)

    def test_pipeline_compound_statement_decomposition(self):
        raw = "ACT-1010: Trenching 200m completed in shift 1 and started lowering at Sec 2; QA clearance pending."
        result = self.service.process_source_payload(
            raw_content=raw,
            file_name="compound_dpr.txt",
            project_id="PRJ-NBG-2026",
            source_type=SourceType.TEXT_DOCUMENT
        )
        self.assertEqual(result.status, "SUCCESS")
        self.assertEqual(len(result.events_extracted), 3)

    def test_pipeline_synthetic_dataset_fixture(self):
        # Test pipeline against synthetic DPR json payload
        synth_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
            "data", "synthetic", "dpr", "dpr_reports.json"
        )
        if os.path.exists(synth_path):
            with open(synth_path) as f:
                payload = f.read()
            res = self.service.process_source_payload(
                raw_content=payload,
                file_name="dpr_reports.json",
                project_id="PRJ-NBG-2026",
                source_type=SourceType.JSON_SYNTHETIC
            )
            self.assertEqual(res.status, "SUCCESS")
            self.assertGreater(len(res.events_extracted), 0)

if __name__ == "__main__":
    unittest.main()
