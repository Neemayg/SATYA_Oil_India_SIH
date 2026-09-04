#!/usr/bin/env python3
"""
SATYA Phase 4 - Synthetic Data Generator
Generates a coherent, deterministic, and highly challenging synthetic dataset
for the fictional project: "North Basin Gas Gathering & Processing Expansion".

DO NOT USE REAL OIL INDIA CONFIDENTIAL DATA. THIS IS 100% SYNTHETIC DATA.
"""

import os
import json
import csv
import random
from datetime import datetime, timedelta

# Fix seed for 100% reproducibility
random.seed(42)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SYNTHETIC_DIR = os.path.join(BASE_DIR, "data", "synthetic")

PROJECT_META = {
    "project_id": "PRJ-NBG-2026",
    "project_name": "North Basin Gas Gathering & Processing Expansion",
    "project_type": "Upstream Gas Gathering & Pipeline Infrastructure",
    "fictional_location": "North Basin Field Sector B, Assam-Arakan Basin (Fictional)",
    "baseline_version": "Rev_01_Baseline",
    "reporting_period": "2026-09-01 to 2026-09-30",
    "disclaimer": "SYNTHETIC DATASET FOR SIH 2026 BENCHMARK EVALUATION ONLY. NO REAL CONFIDENTIAL DATA."
}

DISCIPLINES = ["CIVIL", "PIPING", "MECHANICAL", "ELECTRICAL", "INSTRUMENTATION", "QA_QC", "HSE"]

WBS_HIERARCHY = [
    {"wbs_id": "WBS-100", "parent_id": None, "wbs_code": "NBG", "wbs_name": "North Basin Gas Expansion", "level": 1},
    {"wbs_id": "WBS-200", "parent_id": "WBS-100", "wbs_code": "NBG.GGS3", "wbs_name": "Gas Gathering Station 3 (GGS-3)", "level": 2},
    {"wbs_id": "WBS-210", "parent_id": "WBS-200", "wbs_code": "NBG.GGS3.CIV", "wbs_name": "Civil & Site Development", "level": 3},
    {"wbs_id": "WBS-220", "parent_id": "WBS-200", "wbs_code": "NBG.GGS3.PIP", "wbs_name": "Facility Piping & Manifold", "level": 3},
    {"wbs_id": "WBS-230", "parent_id": "WBS-200", "wbs_code": "NBG.GGS3.MCH", "wbs_name": "Static & Rotating Equipment", "level": 3},
    {"wbs_id": "WBS-240", "parent_id": "WBS-200", "wbs_code": "NBG.GGS3.ELE", "wbs_name": "Electrical & Substation", "level": 3},
    {"wbs_id": "WBS-250", "parent_id": "WBS-200", "wbs_code": "NBG.GGS3.INS", "wbs_name": "Instrumentation & DCS Controls", "level": 3},
    {"wbs_id": "WBS-300", "parent_id": "WBS-100", "wbs_code": "NBG.PL", "wbs_name": "Cross-Country Mainline Pipeline", "level": 2},
    {"wbs_id": "WBS-310", "parent_id": "WBS-300", "wbs_code": "NBG.PL.SEC1", "wbs_name": "Pipeline Section 1 (Km 0.000 to 10.000)", "level": 3},
    {"wbs_id": "WBS-320", "parent_id": "WBS-300", "wbs_code": "NBG.PL.SEC2", "wbs_name": "Pipeline Section 2 (Km 10.000 to 20.000)", "level": 3},
    {"wbs_id": "WBS-330", "parent_id": "WBS-300", "wbs_code": "NBG.PL.HDD", "wbs_name": "Special River HDD Crossings", "level": 3}
]

def generate_activities():
    activities = []
    start_base = datetime(2026, 9, 1)
    act_id_counter = 1010

    # Pipeline Section 1 (Km 0 - 10) - 5 segments x 4 disciplines = 20 L5 activities
    for i in range(1, 6):
        s_km = (i - 1) * 2.0
        e_km = i * 2.0
        p_start = start_base + timedelta(days=(i - 1) * 2)

        # ROW
        activities.append({
            "activity_id": f"ACT-{act_id_counter}",
            "activity_name": f"Mainline ROW Clearing & Grading Sec 1 - Km {s_km:.1f} to {e_km:.1f}",
            "wbs_id": "WBS-310", "wbs_path": "NBG.PL.SEC1", "level": 5, "discipline": "CIVIL",
            "area": "Section 1", "equipment_tag": None, "line_number": "PL-16-01",
            "start_km": s_km, "end_km": e_km,
            "planned_start": p_start.strftime("%Y-%m-%d"),
            "planned_finish": (p_start + timedelta(days=4)).strftime("%Y-%m-%d"),
            "baseline_duration_days": 4, "predecessor_id": None, "successor_id": f"ACT-{act_id_counter+1}",
            "planned_quantity": 2000.0, "unit": "Meters", "is_critical": True
        })
        act_id_counter += 1

        # Trenching
        activities.append({
            "activity_id": f"ACT-{act_id_counter}",
            "activity_name": f"Mainline Trench Excavation Sec 1 - Km {s_km:.1f} to {e_km:.1f}",
            "wbs_id": "WBS-310", "wbs_path": "NBG.PL.SEC1", "level": 5, "discipline": "CIVIL",
            "area": "Section 1", "equipment_tag": "EXC-01", "line_number": "PL-16-01",
            "start_km": s_km, "end_km": e_km,
            "planned_start": (p_start + timedelta(days=2)).strftime("%Y-%m-%d"),
            "planned_finish": (p_start + timedelta(days=6)).strftime("%Y-%m-%d"),
            "baseline_duration_days": 4, "predecessor_id": f"ACT-{act_id_counter-1}", "successor_id": f"ACT-{act_id_counter+1}",
            "planned_quantity": 2000.0, "unit": "Meters", "is_critical": True
        })
        act_id_counter += 1

        # Stringing & Welding
        activities.append({
            "activity_id": f"ACT-{act_id_counter}",
            "activity_name": f"Mainline Pipe Stringing & Welding Sec 1 - Km {s_km:.1f} to {e_km:.1f}",
            "wbs_id": "WBS-310", "wbs_path": "NBG.PL.SEC1", "level": 5, "discipline": "PIPING",
            "area": "Section 1", "equipment_tag": "WELD-CREW-A", "line_number": "PL-16-01",
            "start_km": s_km, "end_km": e_km,
            "planned_start": (p_start + timedelta(days=4)).strftime("%Y-%m-%d"),
            "planned_finish": (p_start + timedelta(days=8)).strftime("%Y-%m-%d"),
            "baseline_duration_days": 4, "predecessor_id": f"ACT-{act_id_counter-1}", "successor_id": f"ACT-{act_id_counter+1}",
            "planned_quantity": 160.0, "unit": "Joints", "is_critical": True
        })
        act_id_counter += 1

        # Lowering & Backfilling
        activities.append({
            "activity_id": f"ACT-{act_id_counter}",
            "activity_name": f"Mainline Lowering & Backfilling Sec 1 - Km {s_km:.1f} to {e_km:.1f}",
            "wbs_id": "WBS-310", "wbs_path": "NBG.PL.SEC1", "level": 5, "discipline": "CIVIL",
            "area": "Section 1", "equipment_tag": "SIDEBOOM-01", "line_number": "PL-16-01",
            "start_km": s_km, "end_km": e_km,
            "planned_start": (p_start + timedelta(days=6)).strftime("%Y-%m-%d"),
            "planned_finish": (p_start + timedelta(days=10)).strftime("%Y-%m-%d"),
            "baseline_duration_days": 4, "predecessor_id": f"ACT-{act_id_counter-1}", "successor_id": None,
            "planned_quantity": 2000.0, "unit": "Meters", "is_critical": True
        })
        act_id_counter += 1

    # Section 2 Pipeline (Km 10 - 20) - 5 segments x 4 disciplines = 20 L5 activities
    for i in range(1, 6):
        s_km = 10.0 + (i - 1) * 2.0
        e_km = 10.0 + i * 2.0
        p_start = start_base + timedelta(days=4 + (i - 1) * 2)

        for act_type, disc, uom, qty in [
            ("ROW Clearing & Grading", "CIVIL", "Meters", 2000.0),
            ("Trench Excavation", "CIVIL", "Meters", 2000.0),
            ("Pipe Stringing & Welding", "PIPING", "Joints", 160.0),
            ("Lowering & Backfilling", "CIVIL", "Meters", 2000.0)
        ]:
            activities.append({
                "activity_id": f"ACT-{act_id_counter}",
                "activity_name": f"Mainline {act_type} Sec 2 - Km {s_km:.1f} to {e_km:.1f}",
                "wbs_id": "WBS-320", "wbs_path": "NBG.PL.SEC2", "level": 5, "discipline": disc,
                "area": "Section 2", "equipment_tag": None, "line_number": "PL-16-02",
                "start_km": s_km, "end_km": e_km,
                "planned_start": p_start.strftime("%Y-%m-%d"),
                "planned_finish": (p_start + timedelta(days=4)).strftime("%Y-%m-%d"),
                "baseline_duration_days": 4, "predecessor_id": None, "successor_id": None,
                "planned_quantity": qty, "unit": uom, "is_critical": False
            })
            act_id_counter += 1

    # GGS-3 Station Activities (Civil, Mechanical, Piping, Electrical, Instrumentation) - 45 activities
    ggs_items = [
        # Civil
        ("GGS-3 Main Site Grading & Earthworks", "CIVIL", "WBS-210", 1.0, "Lot"),
        ("GGS-3 Separator Foundation Concreting V-101", "CIVIL", "WBS-210", 120.0, "Cu.M"),
        ("GGS-3 Pump House Foundation Concreting P-301 A/B", "CIVIL", "WBS-210", 85.0, "Cu.M"),
        ("GGS-3 Compressor Building Foundation K-201", "CIVIL", "WBS-210", 250.0, "Cu.M"),
        ("GGS-3 Boundary Wall & Security Gate Construction", "CIVIL", "WBS-210", 450.0, "Meters"),
        # Mechanical Static & Rotating
        ("GGS-3 Inlet Separator Vessel V-101 Erection", "MECHANICAL", "WBS-230", 1.0, "Item"),
        ("GGS-3 Crude Transfer Pump P-301A Installation", "MECHANICAL", "WBS-230", 1.0, "Item"),
        ("GGS-3 Crude Transfer Pump P-301B Installation", "MECHANICAL", "WBS-230", 1.0, "Item"),
        ("GGS-3 Gas Compressor Package K-201 Erection", "MECHANICAL", "WBS-230", 1.0, "Item"),
        ("GGS-3 Flare Stack Erection & Alignment", "MECHANICAL", "WBS-230", 1.0, "Item"),
        # Facility Piping
        ("GGS-3 Manifold Piping Fabrication 8-inch Line L-101", "PIPING", "WBS-220", 45.0, "Spools"),
        ("GGS-3 Manifold Piping Erection 8-inch Line L-101", "PIPING", "WBS-220", 45.0, "Spools"),
        ("GGS-3 Hydrostatic Testing GGS Manifold Header", "PIPING", "WBS-220", 1.0, "Test"),
        # Electrical
        ("GGS-3 Substation Building Transformer T-01 Erection", "ELECTRICAL", "WBS-240", 1.0, "Item"),
        ("GGS-3 Main Electrical Cable Trench & Cable Pulling", "ELECTRICAL", "WBS-240", 1200.0, "Meters"),
        ("GGS-3 Plant Earthing Grid Installation", "ELECTRICAL", "WBS-240", 800.0, "Meters"),
        # Instrumentation
        ("GGS-3 Control Room DCS Panel Cabinet Erection", "INSTRUMENTATION", "WBS-250", 1.0, "Lot"),
        ("GGS-3 Pressure Transmitter PT-101 Calibration & Fitting", "INSTRUMENTATION", "WBS-250", 1.0, "Item"),
        ("GGS-3 Cold Loop Testing Instrument Loops", "INSTRUMENTATION", "WBS-250", 40.0, "Loops")
    ]

    for item_name, disc, wbs, qty, uom in ggs_items:
        activities.append({
            "activity_id": f"ACT-{act_id_counter}",
            "activity_name": item_name,
            "wbs_id": wbs, "wbs_path": f"NBG.GGS3.{disc[:3]}", "level": 5, "discipline": disc,
            "area": "GGS-3", "equipment_tag": item_name.split()[-1] if len(item_name.split()[-1]) <= 6 else None,
            "line_number": None, "start_km": None, "end_km": None,
            "planned_start": "2026-09-03", "planned_finish": "2026-09-15",
            "baseline_duration_days": 12, "predecessor_id": None, "successor_id": None,
            "planned_quantity": qty, "unit": uom, "is_critical": True
        })
        act_id_counter += 1

    # Special HDD Crossings (2 activities)
    activities.append({
        "activity_id": "ACT-4010",
        "activity_name": "River HDD Crossing Pilot Hole Drilling - Ch 12+400",
        "wbs_id": "WBS-330", "wbs_path": "NBG.PL.HDD", "level": 5, "discipline": "PIPING",
        "area": "River Crossing", "equipment_tag": "HDD-RIG-01", "line_number": "PL-16-HDD",
        "start_km": 12.4, "end_km": 12.8, "planned_start": "2026-09-02", "planned_finish": "2026-09-08",
        "baseline_duration_days": 6, "predecessor_id": None, "successor_id": "ACT-4020",
        "planned_quantity": 400.0, "unit": "Meters", "is_critical": True
    })

    activities.append({
        "activity_id": "ACT-4020",
        "activity_name": "River HDD Crossing 16-inch Pipe Pullback - Ch 12+400",
        "wbs_id": "WBS-330", "wbs_path": "NBG.PL.HDD", "level": 5, "discipline": "PIPING",
        "area": "River Crossing", "equipment_tag": "HDD-RIG-01", "line_number": "PL-16-HDD",
        "start_km": 12.4, "end_km": 12.8, "planned_start": "2026-09-09", "planned_finish": "2026-09-14",
        "baseline_duration_days": 5, "predecessor_id": "ACT-4010", "successor_id": None,
        "planned_quantity": 400.0, "unit": "Meters", "is_critical": True
    })

    return activities

def generate_scenarios():
    scenarios = [
        {"scenario_id": "SCN-001", "name": "Exact Activity ID Match", "difficulty": "EASY", "description": "Field report contains explicit Activity ID (ACT-1010) and matching description.", "expected_outcome": "MATCHED", "expected_confidence": 0.98},
        {"scenario_id": "SCN-002", "name": "Missing Activity ID with Clear Chainage", "difficulty": "MEDIUM", "description": "Field report lacks Activity ID but specifies clear chainage Km 0.0 to 2.0 and action trenching.", "expected_outcome": "MATCHED", "expected_confidence": 0.88},
        {"scenario_id": "SCN-003", "name": "Local Terminology Mismatch (Jargon)", "difficulty": "HARD", "description": "Report says 'HDD 16-inch Pullback' instead of formal WBS title 'River HDD Crossing 16-inch Pipe Pullback'.", "expected_outcome": "MATCHED", "expected_confidence": 0.82},
        {"scenario_id": "SCN-004", "name": "Heavy Acronym & Abbreviation Usage", "difficulty": "HARD", "description": "Report reads 'ROW clrg & grdg Sec 1 Ch 0-2km done'.", "expected_outcome": "MATCHED", "expected_confidence": 0.80},
        {"scenario_id": "SCN-005", "name": "Ambiguous Candidates (Section 1 vs Section 2 Welding)", "difficulty": "HARD", "description": "Report says '12 joints 16in pipe welded' without specifying Section 1 or Section 2.", "expected_outcome": "AMBIGUOUS", "expected_confidence": 0.62},
        {"scenario_id": "SCN-006", "name": "Unmatched Out-of-Scope Field Work", "difficulty": "HARD", "description": "Report states 'Constructed temporary bypass culvert near stream Ch 12+800' (not in baseline).", "expected_outcome": "UNMATCHED", "expected_confidence": 0.20},
        {"scenario_id": "SCN-007", "name": "Contradictory Opposing Reports (Contractor vs. QA NDT)", "difficulty": "HARD", "description": "Contractor DPR claims 100% welding complete; TPIA QA report uploaded same day notes NDT radiography failure on 4 joints.", "expected_outcome": "CONFLICTED", "expected_confidence": 0.50},
        {"scenario_id": "SCN-008", "name": "Near-Duplicate Field Report Re-submission", "difficulty": "MEDIUM", "description": "Same 150m trenching quantities submitted twice in separate DPR transmittals 24h apart.", "expected_outcome": "DUPLICATE_FLAGGED", "expected_confidence": 0.95},
        {"scenario_id": "SCN-009", "name": "Delayed Field Reporting (7-day Transmittal Lag)", "difficulty": "MEDIUM", "description": "Work performed Sept 2 reported in Sept 9 DPR batch.", "expected_outcome": "MATCHED", "expected_confidence": 0.86},
        {"scenario_id": "SCN-010", "name": "Relative Date Phrase Parsing", "difficulty": "MEDIUM", "description": "Report says 'Shift 2 yesterday completed alignment of Vessel V-101'.", "expected_outcome": "MATCHED", "expected_confidence": 0.84},
        {"scenario_id": "SCN-011", "name": "Granularity Mismatch (N micro-events to 1 macro activity)", "difficulty": "HARD", "description": "15 daily shift reports incrementally reporting 10-15 joints welding for 1 macro activity.", "expected_outcome": "MATCHED_AGGREGATED", "expected_confidence": 0.90},
        {"scenario_id": "SCN-012", "name": "Single Report Describing Multiple WBS Activities", "difficulty": "HARD", "description": "Report states 'Cleared ROW and completed 200m trenching at Section 1'.", "expected_outcome": "SPLIT_MATCHED", "expected_confidence": 0.81},
        {"scenario_id": "SCN-013", "name": "Active Critical Path Evidence Gap", "difficulty": "HARD", "description": "Activity ACT-1040 is active on critical path but zero reports received for 8 days.", "expected_outcome": "EVIDENCE_GAP", "expected_confidence": 0.00},
        {"scenario_id": "SCN-014", "name": "Out-of-Sequence Execution Logic Warning", "difficulty": "HARD", "description": "Pipe lowering reported completed before trench excavation activity is reported started.", "expected_outcome": "OUT_OF_SEQUENCE_WARNING", "expected_confidence": 0.55},
        {"scenario_id": "SCN-015", "name": "Independent Corroborating Multi-Source Evidence", "difficulty": "EASY", "description": "DPR entry + attached site photo + QA clearance slip all referencing Pump P-301A erection.", "expected_outcome": "MATCHED_VERIFIED", "expected_confidence": 0.97}
    ]
    return scenarios

def main():
    print("Generating SATYA Phase 4 Synthetic Datasets...")
    
    # Ensure directories exist
    dirs = [
        "schedules", "dpr", "discipline-reports", "site-diaries",
        "supervisor-statements", "voice-transcripts", "historical",
        "ground-truth", "scenarios"
    ]
    for d in dirs:
        os.makedirs(os.path.join(SYNTHETIC_DIR, d), exist_ok=True)
        
    activities = generate_activities()
    scenarios = generate_scenarios()
    
    # Save Baseline Schedule JSON
    schedule_manifest = {
        "project": PROJECT_META,
        "wbs_hierarchy": WBS_HIERARCHY,
        "total_activities": len(activities),
        "activities": activities
    }
    with open(os.path.join(SYNTHETIC_DIR, "schedules", "baseline_schedule.json"), "w") as f:
        json.dump(schedule_manifest, f, indent=2)
        
    # Save Baseline Schedule CSV
    with open(os.path.join(SYNTHETIC_DIR, "schedules", "baseline_schedule.csv"), "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "activity_id", "activity_name", "wbs_id", "wbs_path", "level",
            "discipline", "area", "equipment_tag", "line_number", "start_km", "end_km",
            "planned_start", "planned_finish", "baseline_duration_days",
            "predecessor_id", "successor_id", "planned_quantity", "unit", "is_critical"
        ])
        writer.writeheader()
        writer.writerows(activities)
        
    # Save Scenario Catalog
    with open(os.path.join(SYNTHETIC_DIR, "scenarios", "scenario_catalog.json"), "w") as f:
        json.dump({"total_scenarios": len(scenarios), "scenarios": scenarios}, f, indent=2)
        
    # 2. Build Comprehensive Source Observations for All 15 Scenarios
    dpr_records = []
    ground_truth_dev = []
    ground_truth_eval = []
    ground_truth_edge = []

    scenario_observations = [
        # SCN-001
        ("SRC-001", "DPR_EXCEL", "DPR_2026_09_02_ContractorA.xlsx", "Sheet1!R12", "2026-09-02", "J. Dutta",
         "ACT-1010: Mainline ROW Clearing & Grading Sec 1 - Km 0.0 to 2.0 completed 400m today.", "SCN-001", ["ACT-1010"], "MATCHED", "DEV"),
        # SCN-002
        ("SRC-002", "DPR_PDF", "DPR_2026_09_03_Civil.pdf", "Page 2, Line 15", "2026-09-03", "P. Gogoi",
         "Trench excavation in progress Section 1 from Km 0.0 to 2.0 with 350m dug.", "SCN-002", ["ACT-1011"], "MATCHED", "DEV"),
        # SCN-003
        ("SRC-003", "DPR_PDF", "DPR_2026_09_09_HDD_Team.pdf", "Page 1, Line 8", "2026-09-09", "M. Barua",
         "HDD 16-inch Pullback at river section completed successfully with 400m pipe pulled.", "SCN-003", ["ACT-4020"], "MATCHED", "DEV"),
        # SCN-004
        ("SRC-004", "SUPERVISOR_NOTE", "Supervisor_Notes_Sep02.txt", "Offset 120-210", "2026-09-02", "B. Saikia",
         "ROW clrg & grdg Sec 1 Ch 0-2km done 500m.", "SCN-004", ["ACT-1010"], "MATCHED", "DEV"),
        # SCN-005
        ("SRC-005", "SITE_DIARY", "Site_Log_2026_09_06.txt", "Line 4", "2026-09-06", "R. Sharma",
         "12 joints of 16-inch pipe welding completed near main road crossing.", "SCN-005", ["ACT-1012", "ACT-1016"], "AMBIGUOUS", "EVAL"),
        # SCN-006
        ("SRC-006", "SUPERVISOR_NOTE", "Supervisor_Memo_Sep07.txt", "Offset 0-95", "2026-09-07", "B. Saikia",
         "Constructed temporary timber bypass culvert near stream Ch 12+800 to facilitate crane movement.", "SCN-006", [], "UNMATCHED", "EDGE"),
        # SCN-007
        ("SRC-007A", "DPR_EXCEL", "DPR_2026_09_08_PipingContractor.xlsx", "Sheet1!R8", "2026-09-08", "Contractor A",
         "Mainline Pipe Stringing & Welding Sec 1 Km 0 to 2 (ACT-1012) 100% completed today.", "SCN-007", ["ACT-1012"], "CONFLICTED", "EDGE"),
        # SCN-008
        ("SRC-008", "DPR_EXCEL", "DPR_2026_09_04_ContractorA_v2.xlsx", "Sheet1!R14", "2026-09-04", "Contractor A",
         "Trench excavation Sec 1 Km 0 to 2 completed 350m (duplicate entry).", "SCN-008", ["ACT-1011"], "DUPLICATE_FLAGGED", "EVAL"),
        # SCN-009
        ("SRC-009", "DPR_PDF", "DPR_2026_09_09_Batch.pdf", "Page 5, Line 22", "2026-09-02", "J. Dutta",
         "Mainline ROW Clearing & Grading Sec 1 - Km 0.0 to 2.0 completed 300m on Sept 2.", "SCN-009", ["ACT-1010"], "MATCHED", "EVAL"),
        # SCN-010
        ("SRC-010", "VOICE_TRANSCRIPT", "Voice_Transcript_Sep06.json", "Timestamp 01:14-01:45", "2026-09-06", "M. Hazarika",
         "Shift 2 yesterday completed erection and leveling of GGS-3 Inlet Separator Vessel V-101.", "SCN-010", ["ACT-1050"], "MATCHED", "DEV"),
        # SCN-011
        ("SRC-011", "DPR_EXCEL", "DPR_2026_09_05_ShiftLogs.xlsx", "Sheet3!R2-16", "2026-09-05", "Contractor Crew",
         "Daily shift report 5 of 15: Welded 12 joints on line PL-16-01 Section 1.", "SCN-011", ["ACT-1012"], "MATCHED_AGGREGATED", "EVAL"),
        # SCN-012
        ("SRC-012", "DPR_PDF", "DPR_2026_09_04_MultiWork.pdf", "Page 1, Line 3", "2026-09-04", "P. Gogoi",
         "Cleared 200m ROW and completed 200m trenching at Section 1 Km 2.0 to 4.0.", "SCN-012", ["ACT-1014", "ACT-1015"], "SPLIT_MATCHED", "EVAL"),
        # SCN-013
        ("SRC-013", "SYSTEM_LOG", "Evidence_Gap_Check.json", "Auto-Check", "2026-09-10", "System",
         "Zero field execution reports logged for active critical path task ACT-1013 in last 8 days.", "SCN-013", ["ACT-1013"], "EVIDENCE_GAP", "EDGE"),
        # SCN-014
        ("SRC-014", "SUPERVISOR_NOTE", "Site_Log_Sep05.txt", "Line 18", "2026-09-05", "R. Sharma",
         "Mainline Lowering & Backfilling Sec 1 Km 4.0 to 6.0 completed 150m.", "SCN-014", ["ACT-1019"], "OUT_OF_SEQUENCE_WARNING", "EDGE"),
        # SCN-015
        ("SRC-015", "MULTI_SOURCE", "Multi_Corroboration_Sep06.json", "Composite", "2026-09-06", "TPIA + Site Eng",
         "GGS-3 Crude Transfer Pump P-301A Installation complete with geotagged photo IMG_9012.jpg and TPIA Clearance Cert #QA-9041.", "SCN-015", ["ACT-1051"], "MATCHED_VERIFIED", "DEV")
    ]

    for src_id, stype, fname, loc, rdate, author, snippet, scn_id, exp_acts, exp_out, split in scenario_observations:
        dpr_records.append({
            "source_id": src_id, "source_type": stype, "file_name": fname,
            "locator": loc, "reported_date": rdate, "author": author,
            "raw_snippet": snippet, "scenario_id": scn_id
        })
        gt_item = {
            "source_id": src_id, "scenario_id": scn_id,
            "expected_activity_ids": exp_acts, "expected_outcome": exp_out,
            "raw_snippet": snippet, "split_type": split
        }
        if split == "DEV":
            ground_truth_dev.append(gt_item)
        elif split == "EVAL":
            ground_truth_eval.append(gt_item)
        else:
            ground_truth_edge.append(gt_item)

    # Save DPR Records JSON
    with open(os.path.join(SYNTHETIC_DIR, "dpr", "dpr_reports.json"), "w") as f:
        json.dump({"total_records": len(dpr_records), "records": dpr_records}, f, indent=2)

    # Save Historical Seed Data
    historical_seed = [
        {"entry_id": "MEM-SEED-01", "entry_type": "TERMINOLOGY_ALIAS", "jargon_term": "HDD 16-inch Pullback", "formal_activity_id": "ACT-4020", "formal_activity_name": "River HDD Crossing 16-inch Pipe Pullback - Ch 12+400", "verified_by_planner": "Planner_S_Gogoi", "times_approved": 8},
        {"entry_id": "MEM-SEED-02", "entry_type": "PRODUCTIVITY_RATE", "discipline": "CIVIL", "work_action": "TRENCHING", "planned_rate": "500m/day", "historical_actual_rate": "320m/day", "sample_size_activities": 14}
    ]
    with open(os.path.join(SYNTHETIC_DIR, "historical", "institutional_memory_seed.json"), "w") as f:
        json.dump({"total_seed_entries": len(historical_seed), "entries": historical_seed}, f, indent=2)

    # Save Ground Truth Splits
    with open(os.path.join(SYNTHETIC_DIR, "ground-truth", "ground_truth_dev.json"), "w") as f:
        json.dump({"split": "DEVELOPMENT", "records": ground_truth_dev}, f, indent=2)
        
    with open(os.path.join(SYNTHETIC_DIR, "ground-truth", "ground_truth_eval.json"), "w") as f:
        json.dump({"split": "EVALUATION", "records": ground_truth_eval}, f, indent=2)
        
    with open(os.path.join(SYNTHETIC_DIR, "ground-truth", "ground_truth_edge_cases.json"), "w") as f:
        json.dump({"split": "EDGE_CASES", "records": ground_truth_edge}, f, indent=2)

    print(f"Dataset generated successfully at {SYNTHETIC_DIR}")
    print(f"Total Schedule Activities: {len(activities)}")
    print(f"Total Scenarios: {len(scenarios)}")
    print(f"Total Source Records: {len(dpr_records)}")

if __name__ == "__main__":
    main()
