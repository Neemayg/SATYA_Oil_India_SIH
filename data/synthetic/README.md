# SATYA Phase 4 Synthetic Dataset Specification & Guide

> **Dataset Name:** North Basin Gas Gathering & Processing Expansion (Synthetic)  
> **Governance Status:** Phase 4 Deliverable  
> **Project:** SATYA — Oil India Limited (SIH 2026)  
> **Disclaimer:** **100% SYNTHETIC DATASET FOR SIH 2026 BENCHMARK EVALUATION ONLY. CONTAINS NO REAL OIL INDIA PROPRIETARY OR CONFIDENTIAL DATA.**

---

## 1. Project Overview & Synthetic Context

This dataset represents a fictional upstream energy infrastructure project: **"North Basin Gas Gathering & Processing Expansion"** (`PRJ-NBG-2026`).

It models the structural, spatial, temporal, and semantic relationships between baseline project schedules (Primavera P6 L1–L6 WBS) and heterogeneous field execution observations (DPRs, site diaries, voice transcripts, inspection reports).

```
SYNTHETIC PROJECT METADATA:
  - Project ID: PRJ-NBG-2026
  - Location: North Basin Field Sector B, Assam-Arakan Basin (Fictional)
  - Baseline Version: Rev_01_Baseline
  - Total Activities: 61 L5/L6 Activities across 7 Disciplines
  - Total Scenarios: 15 Domain Challenge Scenarios (SCN-001 to SCN-015)
  - Source Records: 15 Multi-Format Synthetic Observations
```

---

## 2. Directory Structure

```
data/synthetic/
├── README.md                           <-- (This Guide)
├── schedules/
│   ├── baseline_schedule.json          <-- Canonical Baseline Schedule Manifest
│   └── baseline_schedule.csv           <-- Tabular Baseline Schedule Export
├── scenarios/
│   └── scenario_catalog.json           <-- Scenario Definitions & Expected Outcomes
├── dpr/
│   └── dpr_reports.json                <-- Multi-Format Field Observations
├── historical/
│   └── institutional_memory_seed.json  <-- Initial Alias Bank & Historical Rates
└── ground-truth/
    ├── ground_truth_dev.json           <-- Development Dataset Ground Truth
    ├── ground_truth_eval.json          <-- Evaluation Dataset Ground Truth
    └── ground_truth_edge_cases.json    <-- Edge-Case Dataset Ground Truth
```

---

## 3. Scenario Catalog (`SCN-001` to `SCN-015`)

| Scenario ID | Name | Difficulty | Expected Outcome | Core Challenge Tested |
| :--- | :--- | :--- | :--- | :--- |
| **SCN-001** | Exact Activity ID Match | `EASY` | `MATCHED` | Baseline exact Activity ID match (`ACT-1010`). |
| **SCN-002** | Missing Activity ID with Clear Chainage | `MEDIUM` | `MATCHED` | Match without Activity ID using chainage Km 0.0 to 2.0. |
| **SCN-003** | Local Terminology Mismatch (Jargon) | `HARD` | `MATCHED` | Informal site jargon ("HDD 16-inch Pullback"). |
| **SCN-004** | Heavy Acronym & Abbreviation Usage | `HARD` | `MATCHED` | Heavy abbreviations ("ROW clrg & grdg Sec 1 Ch 0-2km"). |
| **SCN-005** | Ambiguous Candidates | `HARD` | `AMBIGUOUS` | 12 joints welding near road crossing matching Sec 1 & Sec 2. |
| **SCN-006** | Unmatched Out-of-Scope Field Work | `HARD` | `UNMATCHED` | Temporary timber bypass culvert not in baseline. |
| **SCN-007** | Contradictory Opposing Reports | `HARD` | `CONFLICTED` | Contractor 100% complete claim vs. TPIA QA NDT failure. |
| **SCN-008** | Near-Duplicate Field Re-submission | `MEDIUM` | `DUPLICATE_FLAGGED` | Same 350m trenching reported twice in 24 hours. |
| **SCN-009** | Delayed Field Reporting | `MEDIUM` | `MATCHED` | Work performed Sept 2 reported in Sept 9 batch. |
| **SCN-010** | Relative Date Phrase Parsing | `MEDIUM` | `MATCHED` | "Shift 2 yesterday completed alignment of Vessel V-101". |
| **SCN-011** | Granularity Mismatch ($N:1$) | `HARD` | `MATCHED_AGGREGATED` | 15 daily shift reports contributing to 1 macro activity. |
| **SCN-012** | Multi-Activity Report ($1:N$) | `HARD` | `SPLIT_MATCHED` | 1 report describing both ROW clearing & trenching. |
| **SCN-013** | Active Critical Path Evidence Gap | `HARD` | `EVIDENCE_GAP` | Zero reports logged for active task ACT-1013 in 8 days. |
| **SCN-014** | Out-of-Sequence Execution Logic | `HARD` | `OUT_OF_SEQUENCE` | Pipe lowering reported before trench excavation complete. |
| **SCN-015** | Corroborating Multi-Source Evidence | `EASY` | `MATCHED_VERIFIED` | DPR entry + geotagged photo + TPIA QA clearance slip. |

---

## 4. Ground Truth Separation Principles

> **CRITICAL ANTI-CHEATING RULE:**  
> The ground truth files in `data/synthetic/ground-truth/` are intended **ONLY for post-execution benchmark evaluation**.  
> Future system components (Extraction Pipeline, Matching Engine, Conflict Engine) **MUST NEVER** read or access ground-truth files during normal processing.

### Dataset Splits
* **`ground_truth_dev.json` (Development Split):** Used during algorithm development to verify basic extraction and matching logic.
* **`ground_truth_eval.json` (Evaluation Split):** Used to measure matching precision, recall, and confidence score calibration on unseen test cases.
* **`ground_truth_edge_cases.json` (Edge-Case Split):** Used to test system resilience against contradictory reports, out-of-sequence execution, and un-scheduled field work.

---

## 5. Dataset Validation & Reproducibility

The dataset is 100% reproducible via the generation script:

```bash
python3 scripts/generate_synthetic_data.py
```

* **Random Seed:** Fixed at `42` for deterministic execution.
* **Integrity Checks Passed:**
  * Zero orphaned activity IDs.
  * 100% WBS parent-child referential integrity.
  * Zero circular CPM logic ties.
  * Unique scenario mappings across ground truth splits.
