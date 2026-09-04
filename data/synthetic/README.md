# SATYA Phase 4 Synthetic Dataset Specification & Guide (Corrected & Expanded)

> **Governance Status:** Phase 4 Deliverable (Fully Corrected & Expanded)  
> **Project:** SATYA — Oil India Limited (SIH 2026)  
> **Disclaimer:** **100% SYNTHETIC DATASET FOR SIH 2026 BENCHMARK EVALUATION ONLY. CONTAINS NO REAL OIL INDIA PROPRIETARY OR CONFIDENTIAL DATA.**

---

## 1. Project Overview & Multi-Project Dataset Scope

Following the Phase 4 Integrity Review, the synthetic dataset has been expanded to include **2 complete, independent fictional project baselines** to test cross-project vocabulary and structural generalization.

```
PROJECT 1: North Basin Gas Gathering & Processing Expansion (PRJ-NBG-2026)
  - Type: Upstream Gas Gathering & Mainline Pipeline
  - Location: North Basin Field Sector B (Fictional)
  - Baseline: Rev_01_Baseline (60 L5/L6 Activities)

PROJECT 2: Subansiri Crude Oil Pipeline Replacement (PRJ-SCP-2026)
  - Type: Cross-Country Crude Trunkline & Tank Farm Infrastructure
  - Location: Subansiri River Sector (Fictional)
  - Baseline: Rev_02_Baseline (41 L5/L6 Activities)

COMBINED DATASET STATS:
  - Total Synthetic Projects: 2 Complete Projects
  - Total Schedule Activities: 101 L5/L6 Activities
  - Total Disciplines Covered: 8 (Civil, Structural, Piping, Mechanical, Electrical, Instrumentation, QA/QC, Safety/HSE)
  - Total Field Observation Records: 107 Observation Documents
  - Ground Truth Splits: 3 (Development: 62, Evaluation: 40, Edge Cases: 5)
```

---

## 2. Directory Structure

```
data/synthetic/
├── README.md                           <-- (This Guide)
├── schedules/
│   ├── baseline_schedule.json          <-- Project 1 Schedule Manifest (PRJ-NBG-2026)
│   ├── project2_baseline_schedule.json <-- Project 2 Schedule Manifest (PRJ-SCP-2026)
│   └── baseline_schedule.csv           <-- Combined CSV Schedule Export (101 Activities)
├── scenarios/
│   └── scenario_catalog.json           <-- 15 Scenario Definitions (SCN-001 to SCN-015)
├── dpr/
│   └── dpr_reports.json                <-- 107 Field Observation Records (Multi-Format)
├── historical/
│   └── institutional_memory_seed.json  <-- Initial Alias Bank & Historical Rates
└── ground-truth/
    ├── ground_truth_dev.json           <-- Development Split (62 Records)
    ├── ground_truth_eval.json          <-- Evaluation Split (40 Records)
    └── ground_truth_edge_cases.json    <-- Edge-Case Split (5 Records)
```

---

## 3. Discipline Coverage Audit (100% Satisfied)

All 8 requested engineering disciplines are explicitly modeled with activities, units of measure, and field observation logs:
1. **Civil:** Site grading, trench excavation, backfilling, Dyke wall construction.
2. **Structural:** Pipe rack steel fabrication & erection, compressor building shelter erection, anchor bolts.
3. **Piping:** Mainline stringing & welding, hydrotesting, manifold spool erection.
4. **Mechanical:** Separator V-101 erection, crude transfer pumps P-301 A/B, compressor package K-201.
5. **Electrical:** Substation transformer T-01, main cable pulling, earthing grid megger test.
6. **Instrumentation:** DCS panel cabinet erection, pressure transmitter PT-101 calibration, cold loop testing.
7. **QA/QC:** Radiography NDT inspection, weld clearance reports.
8. **Safety/HSE:** Fire water ring main trenching, fire monitors & PTW clearances.

---

## 4. Scenario Catalog (`SCN-001` to `SCN-015`)

| Scenario ID | Name | Difficulty | Expected Outcome | Core Challenge Tested |
| :--- | :--- | :--- | :--- | :--- |
| **SCN-001** | Exact Activity ID Match | `EASY` | `MATCHED` | Explicit Activity ID `ACT-1010` in field report. |
| **SCN-002** | Missing Activity ID with Clear Chainage | `MEDIUM` | `MATCHED` | Match without Activity ID using chainage Km 0.0 to 2.0. |
| **SCN-003** | Local Terminology Mismatch (Jargon) | `HARD` | `MATCHED` | Informal site jargon ("HDD 16-inch Pullback"). |
| **SCN-004** | Heavy Acronym & Abbreviation Usage | `HARD` | `MATCHED` | Heavy abbreviations ("ROW clrg & grdg Sec 1 Ch 0-2km"). |
| **SCN-005** | Ambiguous Candidates | `HARD` | `AMBIGUOUS` | Pipe welding near road crossing matching Sec 1 & Sec 2. |
| **SCN-006** | Unmatched Out-of-Scope Field Work | `HARD` | `UNMATCHED` | Construction of temporary timber bypass culvert. |
| **SCN-007** | Contradictory Opposing Reports | `HARD` | `CONFLICTED` | Contractor 100% complete claim vs. TPIA QA NDT failure. |
| **SCN-008** | Near-Duplicate Field Re-submission | `MEDIUM` | `DUPLICATE_FLAGGED` | Same 350m trenching reported twice in 24 hours. |
| **SCN-009** | Delayed Field Reporting | `MEDIUM` | `MATCHED` | Work done Sept 2 reported in Sept 9 batch. |
| **SCN-010** | Relative Date Phrase Parsing | `MEDIUM` | `MATCHED` | "Shift 2 yesterday completed alignment of Vessel V-101". |
| **SCN-011** | Granularity Mismatch ($N:1$) | `HARD` | `MATCHED_AGGREGATED` | 15 daily shift reports for 1 macro activity. |
| **SCN-012** | Multi-Activity Report ($1:N$) | `HARD` | `SPLIT_MATCHED` | Single report describing both ROW clearing & trenching. |
| **SCN-013** | Active Critical Path Evidence Gap | `HARD` | `EVIDENCE_GAP` | Zero reports logged for active task ACT-1013 in 8 days. |
| **SCN-014** | Out-of-Sequence Execution | `HARD` | `OUT_OF_SEQUENCE` | Pipe lowering reported before trench excavation complete. |
| **SCN-015** | Multi-Source Corroboration | `EASY` | `MATCHED_VERIFIED` | DPR entry + geotagged photo + TPIA QA clearance slip. |

---

## 5. Validation & Reproducibility Report

Run validation audit:
```bash
python3 scripts/validate_synthetic_data.py
```

* **Validation Status:** `PASS (100% Integrity Validated)`
* **Reproducibility Script:** `python3 scripts/generate_synthetic_data.py` (Fixed seed `42`).
* **Original Exit Criteria Status:** **GENUINELY SATISFIED** (2 complete project schedules, 101 L5/L6 activities, 107 field observations, 8 disciplines, 3 ground-truth splits).
