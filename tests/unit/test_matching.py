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

    def test_insufficient_evidence_outcome_when_locators_missing(self):
        # Event with vague statement lacking line number, equipment tag, and chainage range
        event = ExecutionEvent(
            event_id="EVT-004", source_id="SRC-004", fragment_id="FRG-004",
            event_type="PROGRESS", observed_timestamp="2026-09-03", source_timestamp="2026-09-03",
            extracted_statement="Execution ongoing for civil task in Section 1.",
            raw_observed_activity_id=None, observed_activity_id=None,
            activity_id_validation_status="NO_EXPLICIT_REFERENCE", discipline="CIVIL",
            area_location="Section 1"
        )
        res = self.engine.match_event_to_fingerprints(event, [self.fp_act1010])
        self.assertEqual(res.outcome, MatchOutcome.INSUFFICIENT_EVIDENCE)
        self.assertIsNone(res.selected_activity_id)
        self.assertIn("line_number_or_equipment_tag", res.missing_discriminators)
        self.assertIn("chainage_km_range", res.missing_discriminators)

    def test_hard_constraint_project_mismatch_elimination(self):
        event = ExecutionEvent(
            event_id="EVT-005", source_id="SRC-005", fragment_id="FRG-005",
            event_type="PROGRESS", observed_timestamp="2026-09-03", source_timestamp="2026-09-03",
            extracted_statement="ROW clearing in Section 1.",
            raw_observed_activity_id=None, observed_activity_id=None,
            discipline="CIVIL", area_location="Section 1"
        )
        # Set event project to another project
        setattr(event, "project_id", "PRJ-OTHER-2026")
        res = self.engine.match_event_to_fingerprints(event, [self.fp_act1010])
        self.assertEqual(res.outcome, MatchOutcome.UNMATCHED)
        self.assertEqual(res.confidence_score, 0.0)

    def test_alias_boost_cannot_bypass_thresholds_or_vocabulary(self):
        """S_alias provides factor ranking boost but CANNOT force match below theta_match or fabricate unknown activities."""
        event = ExecutionEvent(
            event_id="EVT-006", source_id="SRC-006", fragment_id="FRG-006",
            event_type="PROGRESS", observed_timestamp="2026-09-03", source_timestamp="2026-09-03",
            extracted_statement="Unrelated site observation.",
            raw_observed_activity_id=None, observed_activity_id=None,
            discipline="ELECTRICAL", area_location="Section 99"
        )
        # 1. Alias exists for non-existent activity ID
        alias_scores = {"ACT-NONEXISTENT": 1.0, "ACT-1010": 0.5}
        res = self.engine.match_event_to_fingerprints(event, [self.fp_act1010], alias_scores=alias_scores)
        
        # Candidate generation MUST ONLY contain baseline schedule fingerprints
        cand_ids = [c.activity_id for c in res.candidate_matches]
        self.assertNotIn("ACT-NONEXISTENT", cand_ids)

        # 2. Alias boost on low-confidence event cannot force MATCHED outcome if score < theta_match (0.80)
        self.assertEqual(res.outcome, MatchOutcome.UNMATCHED)

if __name__ == "__main__":
    unittest.main()
