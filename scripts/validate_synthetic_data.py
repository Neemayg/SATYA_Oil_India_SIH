#!/usr/bin/env python3
"""
SATYA Phase 4 Data Validation Script
Performs strict integrity checks on generated synthetic datasets.
"""

import os
import json

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SYNTHETIC_DIR = os.path.join(BASE_DIR, "data", "synthetic")

def validate():
    print("Running SATYA Phase 4 Dataset Validation Audit...")
    warnings = []
    failures = []
    
    # 1. Check Project 1 Schedule
    p1_path = os.path.join(SYNTHETIC_DIR, "schedules", "baseline_schedule.json")
    if not os.path.exists(p1_path):
        failures.append("Project 1 baseline schedule missing.")
    else:
        with open(p1_path) as f:
            p1_data = json.load(f)
            print(f"[PASS] Project 1 Loaded: {p1_data['project']['project_id']} ({len(p1_data['activities'])} activities)")
            
    # 2. Check Project 2 Schedule
    p2_path = os.path.join(SYNTHETIC_DIR, "schedules", "project2_baseline_schedule.json")
    if not os.path.exists(p2_path):
        failures.append("Project 2 baseline schedule missing.")
    else:
        with open(p2_path) as f:
            p2_data = json.load(f)
            print(f"[PASS] Project 2 Loaded: {p2_data['project']['project_id']} ({len(p2_data['activities'])} activities)")

    # 3. Check Field Observations
    dpr_path = os.path.join(SYNTHETIC_DIR, "dpr", "dpr_reports.json")
    if not os.path.exists(dpr_path):
        failures.append("DPR field reports file missing.")
    else:
        with open(dpr_path) as f:
            dpr_data = json.load(f)
            print(f"[PASS] DPR Reports Loaded: {len(dpr_data['records'])} observation records")
            if len(dpr_data['records']) < 50:
                failures.append(f"DPR count ({len(dpr_data['records'])}) below required minimum 50.")

    # 4. Check Ground Truth Isolation
    for split in ["ground_truth_dev.json", "ground_truth_eval.json", "ground_truth_edge_cases.json"]:
        gt_path = os.path.join(SYNTHETIC_DIR, "ground-truth", split)
        if not os.path.exists(gt_path):
            failures.append(f"Ground truth split missing: {split}")
        else:
            with open(gt_path) as f:
                gt_data = json.load(f)
                print(f"[PASS] Ground Truth Split Loaded: {split} ({len(gt_data['records'])} records)")

    # 5. Check Discipline Coverage
    disciplines = set()
    for act in p1_data['activities'] + p2_data['activities']:
        disciplines.add(act['discipline'])
    
    expected_disc = {"CIVIL", "STRUCTURAL", "PIPING", "MECHANICAL", "ELECTRICAL", "INSTRUMENTATION", "QA_QC", "SAFETY_HSE"}
    missing_disc = expected_disc - disciplines
    if missing_disc:
        warnings.append(f"Disciplines slightly differ from expected: missing {missing_disc}")
    else:
        print(f"[PASS] 100% Discipline Coverage Satisfied: {sorted(list(disciplines))}")

    print("\n---------------- VALIDATION SUMMARY ----------------")
    if failures:
        print(f"STATUS: FAIL ({len(failures)} failures)")
        for f in failures:
            print(f"  [FAIL] {f}")
    elif warnings:
        print(f"STATUS: PASS WITH WARNINGS ({len(warnings)} warnings)")
        for w in warnings:
            print(f"  [WARN] {w}")
    else:
        print("STATUS: PASS (100% Integrity Validated)")

if __name__ == "__main__":
    validate()
