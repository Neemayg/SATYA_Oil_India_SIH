import unittest
import os
from backend.services.fingerprint_service import ActivityFingerprintService
from backend.persistence.database_engine import DatabaseEngine

class TestFingerprintIntegration(unittest.TestCase):
    def setUp(self):
        self.db = DatabaseEngine(":memory:")
        self.service = ActivityFingerprintService(db_engine=self.db)
        self.base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.schedules_dir = os.path.join(self.base_dir, "data", "synthetic", "schedules")

    def test_load_and_fingerprint_all_synthetic_baseline_schedules(self):
        fps = self.service.load_all_synthetic_schedules(self.schedules_dir)
        
        # Verify 100% of schedule activities across both synthetic projects are fingerprinted
        self.assertGreaterEqual(len(fps), 101)

        # Check project 1 baseline schedule fingerprints
        p1_fps = self.db.get_fingerprints_by_project("PRJ-NBG-2026")
        self.assertGreaterEqual(len(p1_fps), 60)

        # Check project 2 baseline schedule fingerprints
        p2_fps = self.db.get_fingerprints_by_project("PRJ-SCP-2026")
        self.assertEqual(len(p2_fps), 41)

        # Retrieve specific activity fingerprint and verify attributes
        fp_dict = self.db.get_fingerprint_by_activity_id("ACT-1010")
        self.assertIsNotNone(fp_dict)
        self.assertEqual(fp_dict["activity_name"], "Mainline ROW Clearing & Grading Sec 1 - Km 0.0 to 2.0")
        self.assertEqual(fp_dict["discipline"], "CIVIL")
        self.assertIn("Section 1", fp_dict["wbs_name_path"])

    def test_valid_vocabulary_export(self):
        self.service.load_all_synthetic_schedules(self.schedules_dir)
        vocab = self.service.get_valid_activity_vocabulary()
        self.assertIn("ACT-1010", vocab)
        self.assertIn("ACT-SCP-8010", vocab)
        self.assertGreaterEqual(len(vocab), 101)

if __name__ == "__main__":
    unittest.main()
