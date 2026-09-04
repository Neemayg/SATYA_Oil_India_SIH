# SATYA SIH 2026 Live Demo Dataset Specification

**Repository:** SATYA (Schedule-Aligned Truth & Yield Analytics) — Oil India Limited (SIH 2026)  
**Document Path:** `docs/11-sih/demo_data.md`  
**Purpose:** Defines the deterministic, reproducible demo dataset and raw field payloads used during the live 12-minute SIH presentation.

---

## 1. Project & Schedule Context

- **Project ID**: `PRJ-NBG-2026`
- **Project Name**: North Basin Gas Expansion Pipeline (Oil India Limited)
- **Baseline Schedule Source**: `data/synthetic/schedules/baseline_schedule.json`
- **Total Schedule Activities**: 60 activities across 5 WBS levels (L1 to L5)

### Core Demo Activities
| Activity ID | Activity Name | WBS Path | Planned Start | Planned Finish | Planned Qty | UOM | Discipline |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **`ACT-1020`** | Mainline HDD River Crossing Section 3 | `PRJ-NBG-2026 > PL > SEC3` | 2026-09-01 | 2026-09-06 | 450.0 | Meters | PIPING |
| **`ACT-1021`** | Mainline HDD Road Crossing Section 4 | `PRJ-NBG-2026 > PL > SEC4` | 2026-09-05 | 2026-09-10 | 300.0 | Meters | PIPING |
| **`ACT-1018`** | Mainline Trenching & Excavation Sec 3 | `PRJ-NBG-2026 > PL > SEC3` | 2026-08-25 | 2026-08-31 | 1200.0 | Meters | CIVIL |

---

## 2. Hero Field Observation Payload (Observation 1)

### Raw Field DPR Text (`SRC-DEMO-001`)
```text
Daily Progress Report - Duliajan Field Office - Date: 2026-09-04
Contractor: North Basin Constructors Pvt Ltd | Sector: PL-SEC3
"Night shift: HDD Section 3 crossing completed. Approx. 420 m drilling completed on Line PL-16-01. QA/NDT clearance pending due to hydrotest delay. Work reported today, execution started yesterday."
```

### Extracted Execution Events (Decomposed by Layer 1 Pipeline)
1. **Event 1 (`EVT-DEMO-101`)**:
   - **Event Type**: `PROGRESS`
   - **Quantity**: `420.0` Meters
   - **Discipline**: `PIPING`
   - **Area/Location**: `Section 3`
   - **Raw Statement**: *"Approx. 420 m drilling completed on Line PL-16-01."*
2. **Event 2 (`EVT-DEMO-102`)**:
   - **Event Type**: `FINISH`
   - **Area/Location**: `HDD Section 3`
   - **Raw Statement**: *"Night shift: HDD Section 3 crossing completed."*
3. **Event 3 (`EVT-DEMO-103`)**:
   - **Event Type**: `QA_CLEARANCE`
   - **QA Status**: `PENDING`
   - **Raw Statement**: *"QA/NDT clearance pending due to hydrotest delay."*

---

## 3. Matching & Evidence Outputs (Observation 1)

### Matching Engine Outputs (`EVT-DEMO-101` & `EVT-DEMO-102`)
- **Outcome**: `INSUFFICIENT_EVIDENCE` / `AMBIGUOUS` (Confidence Score: **`0.42`**)
- **Selected Activity ID**: `None` (Delegated to Reconciliation Desk)
- **Candidate Activities Surface**:
  1. `ACT-1020` (Mainline HDD River Crossing Section 3): Score **`0.42`** (Matches location "Section 3" & terminology "HDD", but missing explicit Activity ID & QA clearance incomplete).
  2. `ACT-1021` (Mainline HDD Road Crossing Section 4): Score **`0.28`** (Matches "HDD" but location mismatch).
  3. `ACT-1018` (Mainline Trenching Section 3): Score **`0.17`** (Location match only).

### Factor Breakdown for `ACT-1020`
- Identifier Score ($S_{\text{id}}$): **0.00** (No explicit ID present in text)
- Location Score ($S_{\text{loc}}$): **0.80** (Location match: "Section 3")
- Terminology Score ($S_{\text{term}}$): **0.75** (Term match: "HDD crossing")
- Discipline Score ($S_{\text{disc}}$): **1.00** (Discipline: PIPING)
- Temporal Score ($S_{\text{time}}$): **0.90** (Observed timestamp within planned window)
- Alias Boost ($S_{\text{alias}}$): **0.00** (No active terminology alias yet)
- **Combined Score**: **0.42** $< \theta_{\text{match}} = 0.80$ $\rightarrow$ **Delegated to HITL**

---

## 4. Human-in-the-Loop Planner Action

- **Planner ID**: `PLN-DEMO-OIL`
- **Decision Type**: `CHANGE_MATCH`
- **Reviewed Trust Version**: `1`
- **Selected Activity**: `ACT-1020`
- **Override Reason Category**: `TERMINOLOGY_ALIAS`
- **Reason Notes**: *"Field phrase 'HDD Section 3' corresponds to baseline HDD River Crossing Section 3 (`ACT-1020`)."*
- **Resulting Entity Updates**:
  - `ValidationDecision` row appended (`DEC-DEMO-001`)
  - `TrustAssessment` $v2$ created (`TRU-DEMO-002` $\rightarrow$ Status: `TRUSTED`)

---

## 5. Institutional Memory Distillation

### Memory Action 1: Distillation Run
- **Trigger**: Distillation executed after Planner Correction
- **Extracted Terminology Alias Candidate**:
  - Phrase: `"hdd section 3"`
  - Target Activity ID: `ACT-1020`
  - Alias Status: `CANDIDATE` (Single planner decision)

### Memory Action 2: Second Observation (`SRC-DEMO-002`)
```text
Daily Progress Report - Duliajan Field Office - Date: 2026-09-05
Contractor: Assam Pipe Laying Corp | Sector: PL-SEC3
"Second crew update: HDD Section 3 tie-in welding completed on PL-16-01. 30m pull-through done."
```
- Second independent planner / source confirms `"hdd section 3"` $\rightarrow$ `ACT-1020`
- Alias Status promotes: `CANDIDATE` $\rightarrow$ `VALIDATED` $\rightarrow$ `ACTIVE`
- **Future Matching Boost**: Subsequent report containing `"hdd section 3"` receives additive factor boost ($S_{\text{alias}} = +0.25$), elevating total match score above $\theta_{\text{match}} = 0.80$ for automatic matching under policy rules!

---

## 6. Schedule Projection & Time Agent Warning Outputs

### Post-Validation Schedule Projection (`ACT-1020`)
- **Actual Quantity**: `420.0 m` / `450.0 m` (**93.3% Physical Progress**)
- **Planned Finish Date**: `2026-09-06`
- **Projected Finish Date**: `2026-09-09` (Forecast slippage due to pending QA clearance)
- **Schedule Variance ($SV_{\text{finish}}$)**: **+3 days delay**

### Time Agent Temporal Warning Signals Generated
1. **Signal 1 (`SIG-DEMO-001`)**:
   - **Signal Type**: `FORECAST_FINISH_SLIPPAGE`
   - **Severity**: `HIGH`
   - **Target Activity**: `ACT-1020`
   - **Message**: *"Projected finish date (2026-09-09) slips 3 days past baseline finish (2026-09-06)."*
2. **Signal 2 (`SIG-DEMO-002`)**:
   - **Signal Type**: `QA_CLEARANCE_BOTTLENECK`
   - **Severity**: `CRITICAL`
   - **Target Activity**: `ACT-1020`
   - **Message**: *"Physical progress is 93.3% complete but QA clearance remains PENDING. Downstream successor ACT-1025 blocked."*
