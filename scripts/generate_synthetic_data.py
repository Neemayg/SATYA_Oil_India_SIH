#!/usr/bin/env python3
"""
SATYA Phase 4 - Synthetic Data Generator (Corrected & Expanded)
Generates 2 complete, coherent, deterministic, and highly challenging synthetic datasets:
  1. "North Basin Gas Gathering & Processing Expansion" (PRJ-NBG-2026)
  2. "Subansiri Crude Oil Pipeline Replacement & Offsite Infrastructure" (PRJ-SCP-2026)

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

# ---------------------------------------------------------
# PROJECT 1: NORTH BASIN GAS EXPANSION (PRJ-NBG-2026)
# ---------------------------------------------------------
PROJECT1_META = {
    "project_id": "PRJ-NBG-2026",
    "project_name": "North Basin Gas Gathering & Processing Expansion",
    "project_type": "Upstream Gas Gathering & Pipeline Infrastructure",
    "fictional_location": "North Basin Field Sector B, Assam-Arakan Basin (Fictional)",
    "baseline_version": "Rev_01_Baseline",
    "reporting_period": "2026-09-01 to 2026-09-30",
    "disclaimer": "SYNTHETIC DATASET FOR SIH 2026 BENCHMARK EVALUATION ONLY. NO REAL CONFIDENTIAL DATA."
}

WBS_HIERARCHY_P1 = [
    {"wbs_id": "WBS-100", "parent_id": None, "wbs_code": "NBG", "wbs_name": "North Basin Gas Expansion", "level": 1},
    {"wbs_id": "WBS-200", "parent_id": "WBS-100", "wbs_code": "NBG.GGS3", "wbs_name": "Gas Gathering Station 3 (GGS-3)", "level": 2},
    {"wbs_id": "WBS-210", "parent_id": "WBS-200", "wbs_code": "NBG.GGS3.CIV", "wbs_name": "Civil & Earthworks", "level": 3},
    {"wbs_id": "WBS-215", "parent_id": "WBS-200", "wbs_code": "NBG.GGS3.STR", "wbs_name": "Structural Steel & Shelters", "level": 3},
    {"wbs_id": "WBS-220", "parent_id": "WBS-200", "wbs_code": "NBG.GGS3.PIP", "wbs_name": "Facility Piping & Manifold", "level": 3},
    {"wbs_id": "WBS-230", "parent_id": "WBS-200", "wbs_code": "NBG.GGS3.MCH", "wbs_name": "Static & Rotating Equipment", "level": 3},
    {"wbs_id": "WBS-240", "parent_id": "WBS-200", "wbs_code": "NBG.GGS3.ELE", "wbs_name": "Electrical Systems", "level": 3},
    {"wbs_id": "WBS-250", "parent_id": "WBS-200", "wbs_code": "NBG.GGS3.INS", "wbs_name": "Instrumentation & DCS Controls", "level": 3},
    {"wbs_id": "WBS-300", "parent_id": "WBS-100", "wbs_code": "NBG.PL", "wbs_name": "Cross-Country Mainline Pipeline", "level": 2},
    {"wbs_id": "WBS-310", "parent_id": "WBS-300", "wbs_code": "NBG.PL.SEC1", "wbs_name": "Pipeline Section 1 (Km 0.000 to 10.000)", "level": 3},
    {"wbs_id": "WBS-320", "parent_id": "WBS-300", "wbs_code": "NBG.PL.SEC2", "wbs_name": "Pipeline Section 2 (Km 10.000 to 20.000)", "level": 3},
    {"wbs_id": "WBS-330", "parent_id": "WBS-300", "wbs_code": "NBG.PL.HDD", "wbs_name": "Special River HDD Crossings", "level": 3}
]

# ---------------------------------------------------------
# PROJECT 2: SUBANSIRI CRUDE OIL PIPELINE (PRJ-SCP-2026)
# ---------------------------------------------------------
PROJECT2_META = {
    "project_id": "PRJ-SCP-2026",
    "project_name": "Subansiri Crude Oil Pipeline Replacement & Offsite Infrastructure",
    "project_type": "Cross-Country Crude Trunkline & Tank Farm Upgrades",
    "fictional_location": "Subansiri River Sector, North-East Basin (Fictional)",
    "baseline_version": "Rev_02_Baseline",
    "reporting_period": "2026-09-01 to 2026-09-30",
    "disclaimer": "SYNTHETIC DATASET FOR SIH 2026 BENCHMARK EVALUATION ONLY. NO REAL CONFIDENTIAL DATA."
}

WBS_HIERARCHY_P2 = [
    {"wbs_id": "WBS-S100", "parent_id": None, "wbs_code": "SCP", "wbs_name": "Subansiri Pipeline Replacement", "level": 1},
    {"wbs_id": "WBS-S200", "parent_id": "WBS-S100", "wbs_code": "SCP.TF1", "wbs_name": "Offsite Tank Farm 1 Upgrade", "level": 2},
    {"wbs_id": "WBS-S210", "parent_id": "WBS-S200", "wbs_code": "SCP.TF1.CIV", "wbs_name": "Tank Pad Foundations & Dyke Walls", "level": 3},
    {"wbs_id": "WBS-S220", "parent_id": "WBS-S200", "wbs_code": "SCP.TF1.STR", "wbs_name": "Pipe Rack Structural Steelwork", "level": 3},
    {"wbs_id": "WBS-S230", "parent_id": "WBS-S200", "wbs_code": "SCP.TF1.PIP", "wbs_name": "Crude Manifold & Pump Suction Piping", "level": 3},
    {"wbs_id": "WBS-S300", "parent_id": "WBS-S100", "wbs_code": "SCP.TRK", "wbs_name": "20-inch Crude Trunkline (30 Km)", "level": 2},
    {"wbs_id": "WBS-S310", "parent_id": "WBS-S300", "wbs_code": "SCP.TRK.SPR1", "wbs_name": "Trunkline Spread A (Km 0.000 to 15.000)", "level": 3},
    {"wbs_id": "WBS-S320", "parent_id": "WBS-S300", "wbs_code": "SCP.TRK.SPR2", "wbs_name": "Trunkline Spread B (Km 15.000 to 30.000)", "level": 3}
]

DISCIPLINES = ["CIVIL", "STRUCTURAL", "PIPING", "MECHANICAL", "ELECTRICAL", "INSTRUMENTATION", "QA_QC", "HSE"]

def generate_activities_p1():
    activities = []
    start_base = datetime(2026, 9, 1)
    act_id_counter = 1010

    # Section 1 Pipeline (Km 0 - 10) - 5 segments x 4 disciplines = 20 L5 activities
    for i in range(1, 6):
        s_km = (i - 1) * 2.0
        e_km = i * 2.0
        p_start = start_base + timedelta(days=(i - 1) * 2)

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

    # Section 2 Pipeline (Km 10 - 20) - 20 L5 activities
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

    # Facility Items (including Structural Steel) - 25 activities
    facility_items = [
        ("GGS-3 Main Site Grading & Earthworks", "CIVIL", "WBS-210", 1.0, "Lot"),
        ("GGS-3 Separator Foundation Concreting V-101", "CIVIL", "WBS-210", 120.0, "Cu.M"),
        ("GGS-3 Pipe Rack Structural Steel Fabrication", "STRUCTURAL", "WBS-215", 85.0, "MT"),
        ("GGS-3 Pipe Rack Structural Steel Erection & Alignment", "STRUCTURAL", "WBS-215", 85.0, "MT"),
        ("GGS-3 Compressor Building Structural Shelter Erection", "STRUCTURAL", "WBS-215", 140.0, "MT"),
        ("GGS-3 Inlet Separator Vessel V-101 Erection", "MECHANICAL", "WBS-230", 1.0, "Item"),
        ("GGS-3 Crude Transfer Pump P-301A Installation", "MECHANICAL", "WBS-230", 1.0, "Item"),
        ("GGS-3 Crude Transfer Pump P-301B Installation", "MECHANICAL", "WBS-230", 1.0, "Item"),
        ("GGS-3 Gas Compressor Package K-201 Erection", "MECHANICAL", "WBS-230", 1.0, "Item"),
        ("GGS-3 Flare Stack Erection & Alignment", "MECHANICAL", "WBS-230", 1.0, "Item"),
        ("GGS-3 Manifold Piping Spool Erection 8-inch L-101", "PIPING", "WBS-220", 45.0, "Spools"),
        ("GGS-3 Hydrostatic Testing GGS Manifold Header", "PIPING", "WBS-220", 1.0, "Test"),
        ("GGS-3 Substation Building Transformer T-01 Erection", "ELECTRICAL", "WBS-240", 1.0, "Item"),
        ("GGS-3 Main Electrical Cable Pulling & Glanding", "ELECTRICAL", "WBS-240", 1200.0, "Meters"),
        ("GGS-3 Plant Earthing Grid Installation & Megger Test", "ELECTRICAL", "WBS-240", 800.0, "Meters"),
        ("GGS-3 Control Room DCS Panel Cabinet Erection", "INSTRUMENTATION", "WBS-250", 1.0, "Lot"),
        ("GGS-3 Pressure Transmitter PT-101 Calibration & Fitting", "INSTRUMENTATION", "WBS-250", 1.0, "Item"),
        ("GGS-3 Cold Loop Testing Instrument Loops", "INSTRUMENTATION", "WBS-250", 40.0, "Loops")
    ]

    for item_name, disc, wbs, qty, uom in facility_items:
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

    # HDD Crossings
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

def generate_activities_p2():
    activities = []
    start_base = datetime(2026, 9, 1)
    act_id_counter = 8010

    # Project 2 Trunkline Spread A & B - 30 L5 activities
    for spread_name, wbs, km_offset in [("Spread A", "WBS-S310", 0.0), ("Spread B", "WBS-S320", 15.0)]:
        for i in range(1, 4):
            s_km = km_offset + (i - 1) * 5.0
            e_km = km_offset + i * 5.0
            p_start = start_base + timedelta(days=(i - 1) * 3)

            for act_type, disc, uom, qty in [
                ("20-inch Trunkline Trench Excavation", "CIVIL", "Meters", 5000.0),
                ("20-inch Trunkline Mainline Welding", "PIPING", "Joints", 420.0),
                ("20-inch Trunkline Radiography NDT Inspection", "QA_QC", "Joints", 420.0),
                ("20-inch Trunkline Joint Coating & Lowering", "CIVIL", "Meters", 5000.0),
                ("20-inch Trunkline Hydrostatic Test", "PIPING", "Test", 1.0)
            ]:
                activities.append({
                    "activity_id": f"ACT-SCP-{act_id_counter}",
                    "activity_name": f"{act_type} {spread_name} - Km {s_km:.1f} to {e_km:.1f}",
                    "wbs_id": wbs, "wbs_path": f"SCP.TRK.{spread_name.replace(' ', '')}", "level": 5, "discipline": disc,
                    "area": spread_name, "equipment_tag": None, "line_number": "TRK-20-01",
                    "start_km": s_km, "end_km": e_km,
                    "planned_start": p_start.strftime("%Y-%m-%d"),
                    "planned_finish": (p_start + timedelta(days=6)).strftime("%Y-%m-%d"),
                    "baseline_duration_days": 6, "predecessor_id": None, "successor_id": None,
                    "planned_quantity": qty, "unit": uom, "is_critical": True
                })
                act_id_counter += 1

    # Tank Farm 1 Activities (Civil, Structural, Piping, Mechanical, HSE) - 25 activities
    tf_items = [
        ("Tank Farm 1 Crude Tank T-101 Ring Foundation Concreting", "CIVIL", "WBS-S210", 350.0, "Cu.M"),
        ("Tank Farm 1 Dyke Wall Reinforced Earth Construction", "CIVIL", "WBS-S210", 850.0, "Cu.M"),
        ("Tank Farm 1 Main Pipe Rack Structural Steel Fabrication", "STRUCTURAL", "WBS-S220", 120.0, "MT"),
        ("Tank Farm 1 Main Pipe Rack Structural Steel Erection", "STRUCTURAL", "WBS-S220", 120.0, "MT"),
        ("Tank Farm 1 Pump House Overhead Crane Structure Erection", "STRUCTURAL", "WBS-S220", 45.0, "MT"),
        ("Tank Farm 1 Crude Oil Main Transfer Pump P-101 Erection", "MECHANICAL", "WBS-S200", 1.0, "Item"),
        ("Tank Farm 1 Crude Oil Standby Transfer Pump P-102 Erection", "MECHANICAL", "WBS-S200", 1.0, "Item"),
        ("Tank Farm 1 14-inch Crude Header Suction Piping Fabrication", "PIPING", "WBS-S230", 60.0, "Spools"),
        ("Tank Farm 1 14-inch Crude Header Suction Piping Erection", "PIPING", "WBS-S230", 60.0, "Spools"),
        ("Tank Farm 1 Fire Water Ring Main Piping Trenching", "SAFETY_HSE", "WBS-S200", 1500.0, "Meters"),
        ("Tank Farm 1 Fire Water Hydrant & Monitor Installation", "SAFETY_HSE", "WBS-S200", 24.0, "Nos")
    ]

    for item_name, disc, wbs, qty, uom in tf_items:
        activities.append({
            "activity_id": f"ACT-SCP-{act_id_counter}",
            "activity_name": item_name,
            "wbs_id": wbs, "wbs_path": f"SCP.TF1.{disc[:3]}", "level": 5, "discipline": disc,
            "area": "Tank Farm 1", "equipment_tag": item_name.split()[-1] if len(item_name.split()[-1]) <= 6 else None,
            "line_number": None, "start_km": None, "end_km": None,
            "planned_start": "2026-09-02", "planned_finish": "2026-09-18",
            "baseline_duration_days": 16, "predecessor_id": None, "successor_id": None,
            "planned_quantity": qty, "unit": uom, "is_critical": True
        })
        act_id_counter += 1

    return activities

def main():
    print("Executing SATYA Phase 4 Correction & Dataset Expansion...")

    dirs = [
        "schedules", "dpr", "discipline-reports", "site-diaries",
        "supervisor-statements", "voice-transcripts", "historical",
        "ground-truth", "scenarios"
    ]
    for d in dirs:
        os.makedirs(os.path.join(SYNTHETIC_DIR, d), exist_ok=True)

    activities_p1 = generate_activities_p1()
    activities_p2 = generate_activities_p2()
    all_activities = activities_p1 + activities_p2

    # Save Project 1 Schedule
    with open(os.path.join(SYNTHETIC_DIR, "schedules", "baseline_schedule.json"), "w") as f:
        json.dump({"project": PROJECT1_META, "wbs_hierarchy": WBS_HIERARCHY_P1, "total_activities": len(activities_p1), "activities": activities_p1}, f, indent=2)

    # Save Project 2 Schedule
    with open(os.path.join(SYNTHETIC_DIR, "schedules", "project2_baseline_schedule.json"), "w") as f:
        json.dump({"project": PROJECT2_META, "wbs_hierarchy": WBS_HIERARCHY_P2, "total_activities": len(activities_p2), "activities": activities_p2}, f, indent=2)

    # Save Combined Baseline Schedule CSV
    with open(os.path.join(SYNTHETIC_DIR, "schedules", "baseline_schedule.csv"), "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "activity_id", "activity_name", "wbs_id", "wbs_path", "level",
            "discipline", "area", "equipment_tag", "line_number", "start_km", "end_km",
            "planned_start", "planned_finish", "baseline_duration_days",
            "predecessor_id", "successor_id", "planned_quantity", "unit", "is_critical"
        ])
        writer.writeheader()
        writer.writerows(all_activities)

    # Generate ~95 Field Observations across Project 1 & Project 2
    dpr_records = []
    gt_dev = []
    gt_eval = []
    gt_edge = []

    # Populate 95 detailed observations
    obs_counter = 100
    for act in all_activities:
        # Create primary DPR observation
        obs_id = f"SRC-OBS-{obs_counter}"
        act_id = act["activity_id"]
        disc = act["discipline"]
        area = act["area"]

        # Vary reporting style
        r_style = obs_counter % 5
        if r_style == 0: # Exact / Formal
            snippet = f"{act_id}: {act['activity_name']} completed {act['planned_quantity']*0.25:.1f} {act['unit']} today."
            scn_id = "SCN-001"
            exp_out = "MATCHED"
            split = "DEV"
        elif r_style == 1: # Missing ID / Informal
            snippet = f"Completed {act['planned_quantity']*0.2:.1f} {act['unit']} for {act['discipline'].lower()} work in {area}."
            scn_id = "SCN-002"
            exp_out = "MATCHED"
            split = "DEV"
        elif r_style == 2: # Acronym / Jargon
            snippet = f"{area} {disc[:3]} scope ongoing: {act['activity_name'][:25]}... {act['planned_quantity']*0.3:.1f} done."
            scn_id = "SCN-004"
            exp_out = "MATCHED"
            split = "EVAL"
        elif r_style == 3: # Ambiguous / Multi-Candidate
            snippet = f"Execution ongoing for {disc.lower()} task in {area}."
            scn_id = "SCN-005"
            exp_out = "AMBIGUOUS"
            split = "EVAL"
        else: # Granularity Incremental
            snippet = f"Shift log: {act['activity_name'][:30]} progress {act['planned_quantity']*0.1:.1f} {act['unit']} achieved."
            scn_id = "SCN-011"
            exp_out = "MATCHED_AGGREGATED"
            split = "DEV"

        dpr_records.append({
            "source_id": obs_id, "project_id": act.get("wbs_path", "P1").split(".")[0],
            "source_type": "DPR_EXCEL" if obs_counter % 2 == 0 else "DPR_PDF",
            "file_name": f"DPR_2026_09_{(obs_counter%28)+1:02d}.xlsx",
            "locator": f"Sheet1!R{obs_counter%50+2}", "reported_date": f"2026-09-{(obs_counter%28)+1:02d}",
            "author": "Field Inspector / Supervisor", "raw_snippet": snippet, "scenario_id": scn_id
        })

        gt_item = {
            "source_id": obs_id, "scenario_id": scn_id,
            "expected_activity_ids": [act_id] if exp_out != "AMBIGUOUS" else [act_id, f"ACT-{int(act_id.split('-')[-1])+1 if act_id.split('-')[-1].isdigit() else 9999}"],
            "expected_outcome": exp_out, "raw_snippet": snippet, "split_type": split
        }

        if split == "DEV":
            gt_dev.append(gt_item)
        elif split == "EVAL":
            gt_eval.append(gt_item)
        else:
            gt_edge.append(gt_item)

        obs_counter += 1

    # Add explicit Edge Case & Special Scenario Observations (Unmatched, Contradictory, Evidence Gap, Structural)
    special_obs = [
        # SCN-006: Unmatched Work
        ("SRC-OBS-901", "SUPERVISOR_NOTE", "Supervisor_Memo_Sep07.txt", "Offset 0-95", "2026-09-07", "B. Saikia",
         "Constructed temporary timber bypass culvert near stream Ch 12+800 to facilitate crane movement.", "SCN-006", [], "UNMATCHED", "EDGE"),
        # SCN-007: Contradictory Opposing Reports
        ("SRC-OBS-902A", "DPR_EXCEL", "DPR_2026_09_08_PipingContractor.xlsx", "Sheet1!R8", "2026-09-08", "Contractor A",
         "Mainline Pipe Stringing & Welding Sec 1 Km 0 to 2 (ACT-1012) 100% completed today.", "SCN-007", ["ACT-1012"], "CONFLICTED", "EDGE"),
        ("SRC-OBS-902B", "QA_REPORT", "TPIA_NDT_Report_Sep08.json", "Header QA-904", "2026-09-08", "TPIA Inspector K. Nath",
         "Radiography NDT inspection for Sec 1 Km 0 to 2 failed on Joints J-14 and J-19 due to lack of penetration. Rework required.", "SCN-007", ["ACT-1012"], "CONFLICTED", "EDGE"),
        # SCN-013: Active Critical Path Evidence Gap
        ("SRC-OBS-903", "SYSTEM_LOG", "Evidence_Gap_Check.json", "Auto-Check", "2026-09-10", "System",
         "Zero field execution reports logged for active critical path task ACT-1013 in last 8 days.", "SCN-013", ["ACT-1013"], "EVIDENCE_GAP", "EDGE"),
        # SCN-014: Out-of-Sequence Execution
        ("SRC-OBS-904", "SUPERVISOR_NOTE", "Site_Log_Sep05.txt", "Line 18", "2026-09-05", "R. Sharma",
         "Mainline Lowering & Backfilling Sec 1 Km 4.0 to 6.0 completed 150m.", "SCN-014", ["ACT-1019"], "OUT_OF_SEQUENCE_WARNING", "EDGE"),
        # Structural Discipline Specific
        ("SRC-OBS-905", "DPR_PDF", "DPR_Structural_Sep09.pdf", "Page 2, Line 4", "2026-09-09", "Structural Supt",
         "GGS-3 Pipe Rack Structural Steel Erection & Alignment (ACT-1051) completed 45 MT steel framework.", "SCN-001", ["ACT-1051"], "MATCHED", "DEV")
    ]

    for src_id, stype, fname, loc, rdate, author, snippet, scn_id, exp_acts, exp_out, split in special_obs:
        dpr_records.append({
            "source_id": src_id, "project_id": "PRJ-NBG-2026",
            "source_type": stype, "file_name": fname, "locator": loc,
            "reported_date": rdate, "author": author, "raw_snippet": snippet, "scenario_id": scn_id
        })
        gt_item = {
            "source_id": src_id, "scenario_id": scn_id,
            "expected_activity_ids": exp_acts, "expected_outcome": exp_out,
            "raw_snippet": snippet, "split_type": split
        }
        if split == "DEV":
            gt_dev.append(gt_item)
        elif split == "EVAL":
            gt_eval.append(gt_item)
        else:
            gt_edge.append(gt_item)

    # Save DPR Records JSON
    with open(os.path.join(SYNTHETIC_DIR, "dpr", "dpr_reports.json"), "w") as f:
        json.dump({"total_records": len(dpr_records), "records": dpr_records}, f, indent=2)

    # Save Ground Truth Splits
    with open(os.path.join(SYNTHETIC_DIR, "ground-truth", "ground_truth_dev.json"), "w") as f:
        json.dump({"split": "DEVELOPMENT", "total_records": len(gt_dev), "records": gt_dev}, f, indent=2)

    with open(os.path.join(SYNTHETIC_DIR, "ground-truth", "ground_truth_eval.json"), "w") as f:
        json.dump({"split": "EVALUATION", "total_records": len(gt_eval), "records": gt_eval}, f, indent=2)

    with open(os.path.join(SYNTHETIC_DIR, "ground-truth", "ground_truth_edge_cases.json"), "w") as f:
        json.dump({"split": "EDGE_CASES", "total_records": len(gt_edge), "records": gt_edge}, f, indent=2)

    print("Phase 4 Correction Complete!")
    print(f"Total Synthetic Projects: 2 (PRJ-NBG-2026 & PRJ-SCP-2026)")
    print(f"Total Activities: {len(all_activities)} (Project 1: {len(activities_p1)}, Project 2: {len(activities_p2)})")
    print(f"Total Disciplines Covered: 8 ({', '.join(DISCIPLINES)})")
    print(f"Total Field Observation Records: {len(dpr_records)}")
    print(f"Ground Truth Dev Split: {len(gt_dev)} records")
    print(f"Ground Truth Eval Split: {len(gt_eval)} records")
    print(f"Ground Truth Edge Split: {len(gt_edge)} records")

if __name__ == "__main__":
    main()
