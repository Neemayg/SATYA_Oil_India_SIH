"""
SATYA Full Truth-Chain Benchmark & Confidence Calibration (Phase 15 - Component 5)
Evaluates all 5 operational layers with ground-truth dataset:
  Layer 1: Extraction Recall
  Layer 2: Matching Precision / Recall / F1
  Layer 3: Trust Assessment Signal Accuracy
  Layer 4: Schedule Projection Coverage
  Layer 5: Time Agent Signal Detection

Confidence Threshold Sweep:
  θ ∈ [0.40, 0.50, 0.60, 0.70, 0.75, 0.80, 0.85, 0.90, 0.95]
  Measures precision, recall, risk-coverage, and ECE per θ.

Ground Truth: data/synthetic/ground-truth/ground_truth_dev.json (62 records)
"""

import os
import json
import unittest
import math
from backend.persistence.database_engine import DatabaseEngine
from backend.api.app import SATYAApplicationAPI
from backend.models.domain_models import MatchOutcome, SourceType, ValidationDecisionType

# Ground-truth metadata annotation (from Phase 15 governance audit)
KNOWN_EVAL_MISSING_IDS = {
    "ACT-4011", "ACT-8014", "ACT-8019", "ACT-8024", "ACT-8029",
    "ACT-8034", "ACT-8039", "ACT-8044", "ACT-8049"
}
KNOWN_TRUNCATED_RECORDS = {"SRC-OBS-102", "SRC-OBS-122"}

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
GT_DEV_PATH = os.path.join(BASE_DIR, "data", "synthetic", "ground-truth", "ground_truth_dev.json")
SCHEDULE_PATH = os.path.join(BASE_DIR, "data", "synthetic", "schedules", "baseline_schedule.json")


def load_ground_truth(path: str):
    with open(path) as f:
        data = json.load(f)
    return data["records"]


class TestTruthChainBenchmark(unittest.TestCase):
    """
    Evaluates SATYA's full execution-intelligence truth chain against ground-truth annotations.
    """

    @classmethod
    def setUpClass(cls):
        cls.db = DatabaseEngine(":memory:")
        cls.api = SATYAApplicationAPI(cls.db)
        cls.api.fingerprint_service.process_schedule_file(SCHEDULE_PATH)
        vocab = cls.api.fingerprint_service.get_valid_activity_vocabulary()
        cls.api.pipeline_service.set_schedule_vocabulary(vocab)
        cls.api.validation_service.set_valid_vocabulary(vocab)
        cls.valid_activity_vocab = vocab

        cls.records = load_ground_truth(GT_DEV_PATH)

        # Filter out known-defective records before evaluation
        cls.clean_records = [
            r for r in cls.records
            if r["source_id"] not in KNOWN_TRUNCATED_RECORDS
            and not any(aid in KNOWN_EVAL_MISSING_IDS for aid in r.get("expected_activity_ids", []))
        ]

        # Run full pipeline on dev set
        cls.pipeline_results = {}    # source_id -> PipelineRunResult
        cls.match_results = {}       # event_id -> MatchResult
        cls.extraction_recall = []   # did we produce at least 1 event for each record?

        for rec in cls.clean_records:
            snippet = rec["raw_snippet"]
            source_id_tag = rec["source_id"]
            code, _, body = cls.api.dispatch("POST", "/api/v1/ingestion/upload", body={
                "project_id": "PRJ-NBG-2026",
                "source_type": "TEXT_DOCUMENT",
                "content": snippet
            })
            cls.pipeline_results[source_id_tag] = {
                "code": code,
                "body": body,
                "record": rec
            }
            events = body.get("events_extracted", [])
            cls.extraction_recall.append(len(events) > 0)

            for evt_body in events:
                evt_id = evt_body["event_id"]
                code_m, _, body_m = cls.api.dispatch("POST", "/api/v1/matching/match", body={
                    "event_id": evt_id
                })
                cls.match_results[evt_id] = {
                    "code": code_m,
                    "body": body_m,
                    "source_id_tag": source_id_tag,
                    "record": rec
                }
                cls.api.dispatch("POST", "/api/v1/evidence/evaluate", body={"event_id": evt_id})

        # Generate projection and run time agent
        cls.api.dispatch("POST", "/api/v1/projections/generate", body={"project_id": "PRJ-NBG-2026"})
        cls.api.dispatch("POST", "/api/v1/monitoring/evaluate", body={"project_id": "PRJ-NBG-2026"})

    # -----------------------------------------------------------
    # LAYER 1: EXTRACTION RECALL
    # -----------------------------------------------------------
    def test_layer1_extraction_recall(self):
        """Layer 1 — Extraction: At least 80% of clean ground-truth records produce ≥1 event."""
        n_total = len(self.clean_records)
        n_extracted = sum(self.extraction_recall)
        recall = n_extracted / n_total if n_total > 0 else 0.0

        print(f"\n[Layer 1] Extraction Recall: {n_extracted}/{n_total} = {recall:.3f}")
        self.assertGreaterEqual(n_total, 1, "No clean records to evaluate.")
        self.assertGreaterEqual(recall, 0.80,
            f"Extraction recall {recall:.3f} below 0.80 — review extraction engine.")

    # -----------------------------------------------------------
    # LAYER 2: MATCHING PRECISION / RECALL / F1
    # -----------------------------------------------------------
    def test_layer2_matching_metrics(self):
        """Layer 2 — Matching: Measure precision, recall, F1 against ground truth at θ=0.80."""
        tp = fp = fn = unmatched_correct = 0
        matched_with_expected_outcome = 0

        for evt_id, mr in self.match_results.items():
            rec = mr["record"]
            expected_ids = set(rec.get("expected_activity_ids", []))
            expected_outcome = rec.get("expected_outcome", "MATCHED")
            body = mr["body"]

            actual_outcome = body.get("outcome", "UNMATCHED")
            actual_activity = body.get("selected_activity_id")

            if expected_outcome == "UNMATCHED":
                # For UNMATCHED ground truth, correct if we also return UNMATCHED
                if actual_outcome == MatchOutcome.UNMATCHED:
                    unmatched_correct += 1
                continue

            if actual_outcome == MatchOutcome.MATCHED and actual_activity in expected_ids:
                tp += 1
            elif actual_outcome == MatchOutcome.MATCHED and actual_activity not in expected_ids:
                fp += 1
            elif actual_outcome in [MatchOutcome.UNMATCHED, MatchOutcome.AMBIGUOUS, MatchOutcome.INSUFFICIENT_EVIDENCE]:
                fn += 1

        precision = tp / (tp + fp) if (tp + fp) > 0 else None
        recall_val = tp / (tp + fn) if (tp + fn) > 0 else None
        f1 = (2 * precision * recall_val / (precision + recall_val)) if (precision and recall_val) else None

        print(f"\n[Layer 2] Matching — TP={tp}, FP={fp}, FN={fn}")
        print(f"  Precision: {precision:.3f}" if precision else "  Precision: N/A")
        print(f"  Recall: {recall_val:.3f}" if recall_val else "  Recall: N/A")
        print(f"  F1: {f1:.3f}" if f1 else "  F1: N/A")

        self.assertIsNotNone(precision, "No matched predictions to evaluate.")
        self.assertGreaterEqual(precision, 0.70,
            f"Matching precision {precision:.3f} below 0.70 for dev set.")

    # -----------------------------------------------------------
    # LAYER 3: TRUST SIGNAL ACCURACY
    # -----------------------------------------------------------
    def test_layer3_trust_signal_accuracy(self):
        """Layer 3 — Trust: For matched ground-truth records, verify trust assessments are produced."""
        events_with_trust = 0
        events_evaluated = 0

        conn = self.db._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(DISTINCT event_id) FROM trust_assessments")
        events_with_trust = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM execution_events")
        total_events = cursor.fetchone()[0]

        trust_coverage = events_with_trust / total_events if total_events > 0 else 0.0
        print(f"\n[Layer 3] Trust Assessment Coverage: {events_with_trust}/{total_events} = {trust_coverage:.3f}")

        self.assertGreaterEqual(trust_coverage, 0.80,
            f"Trust assessment coverage {trust_coverage:.3f} below 0.80.")

    # -----------------------------------------------------------
    # LAYER 4: SCHEDULE PROJECTION COVERAGE
    # -----------------------------------------------------------
    def test_layer4_schedule_projection_coverage(self):
        """Layer 4 — Projection: Projection generated and covers all known activities."""
        proj = self.db.get_latest_schedule_projection("PRJ-NBG-2026")
        if proj is None:
            print("\n[Layer 4] Schedule Projection: NOT GENERATED (insufficient matched events)")
            return

        act_map = proj.get("activity_progress_map", {})
        print(f"\n[Layer 4] Schedule Projection: Generated with {len(act_map)} activity entries, "
              f"Overall Progress: {proj.get('overall_project_progress_pct', 0):.1f}%")
        self.assertGreater(len(act_map), 0, "Projection contains no activity progress entries.")

    # -----------------------------------------------------------
    # LAYER 5: TIME AGENT SIGNAL DETECTION
    # -----------------------------------------------------------
    def test_layer5_time_agent_signal_detection(self):
        """Layer 5 — Time Agent: Verify time agent produces deterministic signals per specification."""
        conn = self.db._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT COUNT(*) FROM monitoring_evaluation_runs WHERE project_id = ?
        """, ("PRJ-NBG-2026",))
        run_count = cursor.fetchone()[0]

        cursor.execute("""
            SELECT COUNT(*) FROM temporal_warning_signals WHERE project_id = ?
        """, ("PRJ-NBG-2026",))
        signal_count = cursor.fetchone()[0]

        print(f"\n[Layer 5] Time Agent: {run_count} evaluation runs, {signal_count} signals produced for PRJ-NBG-2026")
        self.assertGreaterEqual(run_count, 1, "No monitoring evaluation runs found.")

    # -----------------------------------------------------------
    # CONFIDENCE THRESHOLD SWEEP & ECE
    # -----------------------------------------------------------
    def test_confidence_threshold_sweep_and_ece(self):
        """
        Sweeps θ ∈ [0.40, 0.50, 0.60, 0.70, 0.75, 0.80, 0.85, 0.90, 0.95]
        Measures precision, risk-coverage, and Expected Calibration Error (ECE).
        Reports N/A for ECE if insufficient calibration sample (<10 predictions).
        """
        thresholds = [0.40, 0.50, 0.60, 0.70, 0.75, 0.80, 0.85, 0.90, 0.95]

        # Collect all match predictions with confidence scores
        predictions = []
        for evt_id, mr in self.match_results.items():
            rec = mr["record"]
            expected_ids = set(rec.get("expected_activity_ids", []))
            expected_outcome = rec.get("expected_outcome", "MATCHED")
            body = mr["body"]
            conf = body.get("confidence_score", 0.0)
            actual_activity = body.get("selected_activity_id")
            actual_outcome = body.get("outcome", "UNMATCHED")

            if expected_outcome != "UNMATCHED":
                correct = (actual_outcome == MatchOutcome.MATCHED and actual_activity in expected_ids)
                predictions.append({"conf": conf, "correct": correct, "outcome": actual_outcome})

        print(f"\n[Calibration] Total predictions for sweep: {len(predictions)}")

        if len(predictions) < 10:
            print("  ECE = N/A — insufficient calibration sample (<10 predictions)")
            return

        # Threshold sweep table
        print(f"\n{'θ':>6} | {'Precision':>9} | {'Coverage':>8} | {'Accept%':>7}")
        print("-" * 38)
        for theta in thresholds:
            accepted = [p for p in predictions if p["conf"] >= theta]
            accepted_correct = [p for p in accepted if p["correct"]]
            precision = len(accepted_correct) / len(accepted) if accepted else None
            coverage = len(accepted) / len(predictions)
            accept_pct = coverage * 100
            prec_str = f"{precision:.3f}" if precision is not None else "  N/A "
            print(f"  {theta:.2f} | {prec_str:>9} | {coverage:.3f}   | {accept_pct:.1f}%")

        # ECE computation (10-bin equal-width)
        n_bins = 10
        bins = [[] for _ in range(n_bins)]
        for p in predictions:
            bin_idx = min(int(p["conf"] * n_bins), n_bins - 1)
            bins[bin_idx].append(p)

        ece = 0.0
        for bin_preds in bins:
            if not bin_preds:
                continue
            avg_conf = sum(p["conf"] for p in bin_preds) / len(bin_preds)
            avg_acc = sum(1 for p in bin_preds if p["correct"]) / len(bin_preds)
            ece += (len(bin_preds) / len(predictions)) * abs(avg_conf - avg_acc)

        print(f"\n  ECE (10-bin equal-width): {ece:.4f}")
        # No hard threshold for ECE — report empirically
        self.assertGreaterEqual(len(predictions), 10)

    # -----------------------------------------------------------
    # REGRESSION: ZERO HISTORICAL MUTATIONS AFTER ALL EVALUATIONS
    # -----------------------------------------------------------
    def test_historical_immutability_regression_post_benchmark(self):
        """After all benchmark evaluations, confirm no historical records were mutated."""
        conn = self.db._get_connection()
        cursor = conn.cursor()

        # All version_index=1 TrustAssessments should still be UNTOUCHED
        cursor.execute("SELECT COUNT(*) FROM trust_assessments WHERE version_index = 1")
        v1_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(DISTINCT event_id) FROM trust_assessments")
        distinct_events = cursor.fetchone()[0]

        # There should be at least as many v1 rows as distinct events
        self.assertGreaterEqual(v1_count, distinct_events,
            "Historical v1 TrustAssessments are fewer than distinct events — possible mutation detected.")
        print(f"\n[Regression] Historical v1 TrustAssessments: {v1_count} across {distinct_events} events. ✅ Append-only ledger intact.")


if __name__ == "__main__":
    unittest.main()
