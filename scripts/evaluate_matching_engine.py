"""
SATYA Ground Truth Benchmark Evaluation Script
Evaluates the Schedule-Aware Matching Engine against synthetic ground truth datasets
(ground_truth_dev.json, ground_truth_edge_cases.json, ground_truth_eval.json) and calculates:
- Top-1 Match Precision & Accuracy
- Top-3 Candidate Recall
- Ambiguous Detection Rate
- Unmatched Detection Rate
"""

import os
import json
import sys
from typing import Dict, Any, List

# Add repository root to python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.persistence.database_engine import DatabaseEngine
from backend.services.fingerprint_service import ActivityFingerprintService
from backend.services.pipeline_service import ExecutionEventPipelineService
from backend.services.matching_service import ScheduleMatchingService
from backend.models.domain_models import SourceType, MatchOutcome

def run_evaluation(ground_truth_path: str, db_engine: DatabaseEngine) -> Dict[str, Any]:
    """Runs matching evaluation against a specified ground truth JSON file."""
    if not os.path.exists(ground_truth_path):
        return {"error": f"File not found: {ground_truth_path}"}

    with open(ground_truth_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    records = data.get("records", [])
    split_name = data.get("split", "UNKNOWN")

    pipeline_service = ExecutionEventPipelineService(db_engine=db_engine)
    matching_service = ScheduleMatchingService(db_engine=db_engine)
    fp_service = ActivityFingerprintService(db_engine=db_engine)
    pipeline_service.set_schedule_vocabulary(fp_service.get_valid_activity_vocabulary())

    total = len(records)
    correct_top1 = 0
    correct_top3 = 0
    ambiguous_detected = 0
    unmatched_detected = 0
    expected_unmatched = 0

    for rec in records:
        snippet = rec.get("raw_snippet", "")
        expected_act_ids = [act.upper() for act in rec.get("expected_activity_ids", [])]
        expected_outcome = rec.get("expected_outcome", "MATCHED")

        if expected_outcome == "UNMATCHED":
            expected_unmatched += 1

        # Process raw snippet through pipeline
        run_res = pipeline_service.process_source_payload(
            raw_content=snippet,
            file_name=f"eval_{rec.get('source_id', 'SRC')}.txt",
            project_id="PRJ-NBG-2026",
            source_type=SourceType.TEXT_DOCUMENT
        )

        if not run_res.events_extracted:
            if expected_outcome == "UNMATCHED":
                unmatched_detected += 1
                correct_top1 += 1
            continue

        event = run_res.events_extracted[0]
        match_res = matching_service.match_event(event)

        # Evaluate against expected
        if match_res.outcome == MatchOutcome.MATCHED:
            if match_res.selected_activity_id in expected_act_ids:
                correct_top1 += 1
                correct_top3 += 1
        elif match_res.outcome == MatchOutcome.AMBIGUOUS:
            ambiguous_detected += 1
            cand_ids = [c.activity_id for c in match_res.candidate_matches[:3]]
            if any(act in expected_act_ids for act in cand_ids):
                correct_top3 += 1
        elif match_res.outcome == MatchOutcome.UNMATCHED:
            unmatched_detected += 1
            if expected_outcome == "UNMATCHED" or not expected_act_ids:
                correct_top1 += 1
                correct_top3 += 1

    top1_precision = round((correct_top1 / total) * 100, 2) if total > 0 else 0.0
    top3_recall = round((correct_top3 / total) * 100, 2) if total > 0 else 0.0

    return {
        "split": split_name,
        "total_records": total,
        "correct_top1": correct_top1,
        "top1_precision_pct": top1_precision,
        "correct_top3": correct_top3,
        "top3_recall_pct": top3_recall,
        "ambiguous_detected": ambiguous_detected,
        "unmatched_detected": unmatched_detected,
        "expected_unmatched": expected_unmatched
    }

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    gt_dir = os.path.join(base_dir, "data", "synthetic", "ground-truth")
    sched_dir = os.path.join(base_dir, "data", "synthetic", "schedules")

    # In-memory database with pre-indexed activity fingerprints
    db = DatabaseEngine(":memory:")
    fp_service = ActivityFingerprintService(db_engine=db)
    fp_service.load_all_synthetic_schedules(sched_dir)

    print("==================================================")
    print("SATYA MATCHING ENGINE BENCHMARK EVALUATION")
    print("==================================================")

    for gt_file in ["ground_truth_dev.json", "ground_truth_edge_cases.json", "ground_truth_eval.json"]:
        gt_path = os.path.join(gt_dir, gt_file)
        res = run_evaluation(gt_path, db)
        print(f"\nBenchmark Split: {res.get('split')} ({gt_file})")
        print(f"Total Records Evaluated: {res.get('total_records')}")
        print(f"Top-1 Precision:         {res.get('top1_precision_pct')}% ({res.get('correct_top1')}/{res.get('total_records')})")
        print(f"Top-3 Recall:            {res.get('top3_recall_pct')}% ({res.get('correct_top3')}/{res.get('total_records')})")
        print(f"Ambiguous Flags:         {res.get('ambiguous_detected')}")
        print(f"Unmatched Flags:         {res.get('unmatched_detected')} (Expected: {res.get('expected_unmatched')})")

    print("\n==================================================")

if __name__ == "__main__":
    main()
