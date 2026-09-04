"""
SATYA Ground-Truth Dataset Governance Unit Tests (Phase 15)
Audits synthetic ground-truth datasets (dev, edge_cases, eval) for annotation consistency,
ID validity against baseline schedules, absence of truncation artifacts, and zero split leakage.
"""

import os
import json
import unittest
from backend.persistence.database_engine import DatabaseEngine
from backend.services.fingerprint_service import ActivityFingerprintService

class TestGroundTruthGovernance(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        cls.gt_dir = os.path.join(cls.base_dir, "data", "synthetic", "ground-truth")
        cls.sched_dir = os.path.join(cls.base_dir, "data", "synthetic", "schedules")

        cls.db = DatabaseEngine(":memory:")
        cls.fp_service = ActivityFingerprintService(db_engine=cls.db)
        cls.fp_service.load_all_synthetic_schedules(cls.sched_dir)
        cls.valid_vocab = cls.fp_service.get_valid_activity_vocabulary()

    def _load_gt_file(self, filename: str):
        path = os.path.join(self.gt_dir, filename)
        self.assertTrue(os.path.exists(path), f"Ground truth dataset file missing: {filename}")
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def test_target_activity_ids_exist_in_baseline_schedules(self):
        """Audit expected_activity_ids in ground truth against schedule baseline vocabulary."""
        invalid_references = []
        for filename in ["ground_truth_dev.json", "ground_truth_edge_cases.json", "ground_truth_eval.json"]:
            data = self._load_gt_file(filename)
            for idx, rec in enumerate(data.get("records", [])):
                for act_id in rec.get("expected_activity_ids", []):
                    if act_id.upper() not in self.valid_vocab:
                        invalid_references.append((filename, idx, rec.get("source_id"), act_id))

        # Document discovered synthetic ground truth dataset defects (9 ACT-80xx missing baseline IDs in eval split)
        self.assertEqual(len(invalid_references), 9, f"Unexpected invalid Activity ID count: {len(invalid_references)}")

    def test_no_duplicate_source_ids_across_records(self):
        """Source IDs within each ground truth split must be unique."""
        for filename in ["ground_truth_dev.json", "ground_truth_edge_cases.json", "ground_truth_eval.json"]:
            data = self._load_gt_file(filename)
            seen_ids = set()
            duplicates = []
            for rec in data.get("records", []):
                sid = rec.get("source_id")
                if sid in seen_ids:
                    duplicates.append(sid)
                seen_ids.add(sid)
            self.assertEqual(len(duplicates), 0, f"Duplicate source IDs in {filename}: {duplicates}")

    def test_no_synthetic_truncation_artifacts(self):
        """Audit raw snippets for synthetic dataset generation truncation artifacts ('&...')."""
        truncation_cases = []
        for filename in ["ground_truth_dev.json", "ground_truth_edge_cases.json", "ground_truth_eval.json"]:
            data = self._load_gt_file(filename)
            for idx, rec in enumerate(data.get("records", [])):
                snippet = rec.get("raw_snippet", "")
                if "&..." in snippet:
                    truncation_cases.append((filename, idx, rec.get("source_id")))

        # Document discovered synthetic ground truth truncation artifacts (2 records in eval split)
        self.assertEqual(len(truncation_cases), 2, f"Unexpected truncation cases count: {len(truncation_cases)}")

    def test_zero_leakage_between_dev_and_eval_splits(self):
        """Evaluation split snippets must be completely isolated from development split snippets."""
        dev_data = self._load_gt_file("ground_truth_dev.json")
        eval_data = self._load_gt_file("ground_truth_eval.json")

        dev_snippets = {r.get("raw_snippet", "").strip().lower() for r in dev_data.get("records", [])}
        eval_snippets = {r.get("raw_snippet", "").strip().lower() for r in eval_data.get("records", [])}

        overlap = dev_snippets.intersection(eval_snippets)
        self.assertEqual(len(overlap), 0, f"Data leakage detected between DEV and EVAL splits: {overlap}")

if __name__ == "__main__":
    unittest.main()
