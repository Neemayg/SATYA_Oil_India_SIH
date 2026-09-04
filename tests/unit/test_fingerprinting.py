import unittest
from backend.fingerprinting.terminology_engine import TerminologyIntelligenceEngine
from backend.fingerprinting.fingerprint_generator import ActivityFingerprintGenerator

class TestActivityFingerprinting(unittest.TestCase):
    def setUp(self):
        self.term_engine = TerminologyIntelligenceEngine()
        self.generator = ActivityFingerprintGenerator()

    def test_abbreviation_expansion(self):
        text = "ROW Clearing and HDD River Crossing for PL-16"
        expansions = self.term_engine.expand_abbreviations(text)
        self.assertIn("Right of Way", expansions)
        self.assertIn("Horizontal Directional Drilling", expansions)

    def test_action_verb_and_noun_extraction(self):
        text = "Mainline Pipe Stringing & Welding Sec 1 - Km 0.0 to 2.0"
        verbs = self.term_engine.extract_action_verbs(text)
        self.assertIn("welding", verbs)
        self.assertIn("stringing", verbs)

        nouns = self.term_engine.extract_entity_nouns(text)
        self.assertIn("mainline", nouns)

    def test_wbs_name_path_generation(self):
        wbs_hierarchy = [
            {"wbs_id": "WBS-100", "parent_id": None, "wbs_name": "North Basin Gas Expansion"},
            {"wbs_id": "WBS-300", "parent_id": "WBS-100", "wbs_name": "Cross-Country Mainline Pipeline"},
            {"wbs_id": "WBS-310", "parent_id": "WBS-300", "wbs_name": "Pipeline Section 1"}
        ]
        lookup = self.generator.build_wbs_lookup(wbs_hierarchy)
        path = self.generator.get_wbs_name_path("WBS-310", lookup)
        self.assertEqual(path, "North Basin Gas Expansion > Cross-Country Mainline Pipeline > Pipeline Section 1")

    def test_single_activity_fingerprint_generation(self):
        wbs_hierarchy = [
            {"wbs_id": "WBS-100", "parent_id": None, "wbs_name": "North Basin Gas Expansion"},
            {"wbs_id": "WBS-310", "parent_id": "WBS-100", "wbs_name": "Pipeline Section 1"}
        ]
        lookup = self.generator.build_wbs_lookup(wbs_hierarchy)

        act = {
            "activity_id": "ACT-1010",
            "activity_name": "Mainline ROW Clearing & Grading Sec 1",
            "wbs_id": "WBS-310",
            "wbs_path": "NBG.PL.SEC1",
            "discipline": "CIVIL",
            "area": "Section 1",
            "planned_start": "2026-09-01",
            "planned_finish": "2026-09-05",
            "baseline_duration_days": 4,
            "planned_quantity": 2000.0,
            "unit": "Meters",
            "is_critical": True,
            "predecessor_id": None,
            "successor_id": "ACT-1011"
        }

        fp = self.generator.generate_fingerprint(act, "PRJ-NBG-2026", lookup)
        self.assertEqual(fp.activity_id, "ACT-1010")
        self.assertEqual(fp.wbs_name_path, "North Basin Gas Expansion > Pipeline Section 1")
        self.assertIn("clearing", fp.action_verbs)
        self.assertEqual(fp.discipline, "CIVIL")
        self.assertTrue(fp.is_critical)
        self.assertIn("row clearing", fp.field_aliases)
        self.assertIn("right of way", fp.field_aliases)

if __name__ == "__main__":
    unittest.main()
