import unittest
from backend.matching.matching_engine import ScheduleAwareMatchingEngine
from backend.models.domain_models import ExecutionEvent, ActivityFingerprint, MatchOutcome

class TestScheduleMatchingEngine(unittest.TestCase):
    def setUp(self):
        self.engine = ScheduleAwareMatchingEngine(theta_match=0.80, theta_unmatched=0.45)
        self.fp_act1010 = ActivityFingerprint(
            fingerprint_id="FPT-ACT-1010",
            activity_id="ACT-1010",
            project_id="PRJ-NBG-2026",
            activity_name="Mainline ROW Clearing & Grading Sec 1 - Km 0.0 to 2.0",
            normalized_name="Mainline ROW Clearing & Grading Sec 1 - Km 0.0 to 2.0",
            wbs_id="WBS-310",
            wbs_code="NBG.PL.SEC1",
            wbs_name_path="North Basin Gas Expansion > Mainline Pipeline > Pipeline Section 1",
            discipline="CIVIL",
            area_location="Section 1",
            line_number="PL-16-01",
            planned_start="2026-09-01",
            planned_finish="2026-09-05",
            baseline_duration_days=4,
            planned_quantity=2000.0,
            unit_of_measure="Meters",
            is_critical=True,
            action_verbs=["clearing", "grading"],
            entity_nouns=["mainline", "row", "pipeline"],
            synonyms=["right of way", "ground levelling"],
            field_aliases=["row prep", "bush clearing"]
        )

    def test_exact_activity_id_match_produces_matched_outcome(self):
        event = ExecutionEvent(
            event_id="EVT-001", source_id="SRC-001", fragment_id="FRG-001",
            event_type="FINISH", observed_timestamp="2026-09-02", source_timestamp="2026-09-02",
            extracted_statement="ACT-1010 ROW clearing completed 400m.",
            raw_observed_activity_id="ACT-1010", observed_activity_id="ACT-1010",
            activity_id_validation_status="VALID_SCHEDULE_ID", discipline="CIVIL",
            area_location="Section 1", observed_quantity=400.0, unit_of_measure="Meters"
        )
        res = self.engine.match_event_to_fingerprints(event, [self.fp_act1010])
        self.assertEqual(res.outcome, MatchOutcome.MATCHED)
        self.assertEqual(res.selected_activity_id, "ACT-1010")
        self.assertGreaterEqual(res.confidence_score, 0.90)
        self.assertIn("Explicit Activity ID 'ACT-1010' matches", res.reasoning_trace[2])

    def test_missing_activity_id_multi_factor_match(self):
        # Event with NO Activity ID, relying on discipline + area + action verb alignment
        event = ExecutionEvent(
            event_id="EVT-002", source_id="SRC-002", fragment_id="FRG-002",
            event_type="PROGRESS", observed_timestamp="2026-09-03", source_timestamp="2026-09-03",
            extracted_statement="ROW clearing and grading in Section 1 line PL-16-01 achieved 500m.",
            raw_observed_activity_id=None, observed_activity_id=None,
            activity_id_validation_status="NO_EXPLICIT_REFERENCE", discipline="CIVIL",
            area_location="Section 1", line_number="PL-16-01", observed_quantity=500.0
        )
        res = self.engine.match_event_to_fingerprints(event, [self.fp_act1010])
        self.assertEqual(res.outcome, MatchOutcome.MATCHED)
        self.assertEqual(res.selected_activity_id, "ACT-1010")
        self.assertGreaterEqual(res.confidence_score, 0.80)

    def test_unmatched_out_of_domain_observation(self):
        event = ExecutionEvent(
            event_id="EVT-003", source_id="SRC-003", fragment_id="FRG-003",
            event_type="UNKNOWN", observed_timestamp="2026-09-02", source_timestamp="2026-09-02",
            extracted_statement="Constructed temporary timber bypass culvert near stream Ch 12+800.",
            raw_observed_activity_id=None, observed_activity_id=None,
            discipline="CIVIL", area_location="Ch 12+800"
        )
        res = self.engine.match_event_to_fingerprints(event, [self.fp_act1010])
        self.assertEqual(res.outcome, MatchOutcome.UNMATCHED)
        self.assertIsNone(res.selected_activity_id)
        self.assertLess(res.confidence_score, 0.45)

if __name__ == "__main__":
    unittest.main()
