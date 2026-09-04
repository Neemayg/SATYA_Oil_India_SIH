# End-to-End User Journeys & Product State Model

> **Document Type:** Operational User Journeys & State Progression Model  
> **Governance Status:** Phase 2 Deliverable  
> **Project:** SATYA — Oil India Limited (SIH 2026)  

---

## 1. Product State Progression Model

In SATYA, execution intelligence moves through 5 explicit operational states. State transitions are deterministic, audit-logged, and reversible under planner supervision.

```
+---------------+      +---------------+      +---------------+      +---------------+      +-----------------------+
|   OBSERVED    | ---> |   EXTRACTED   | ---> |    MATCHED    | ---> |   VALIDATED   | ---> | PROJECTED TO SCHEDULE |
+---------------+      +---------------+      +---------------+      +---------------+      +-----------------------+
 Raw file ingested     Parsed event           Linked to candidate    Evidence verified      Primavera actuals
 into immutable        created with           activity fingerprint   & HITL approved        updated / S-curve
 storage               provenance             (or UNMATCHED)                                recalculated
```

### State Progression Specification

| State Name | Definition | Transition Trigger | Information Required | Reversibility |
| :--- | :--- | :--- | :--- | :--- |
| **`OBSERVED`** | Raw field observation file ingested and archived immutably. | Ingestion API / File Upload | Raw file bytes, file metadata, ingestion timestamp. | Immutable (Cannot be deleted or mutated). |
| **`EXTRACTED`** | Structured `ExecutionEvent` entity parsed from raw input. | Entity Extractor Pipeline | Work action, observed quantity, location/chainage, raw snippet. | Reversible (Can be re-parsed if extractor model updates). |
| **`MATCHED`** | Link established between event and candidate Activity ID(s), or marked `UNMATCHED`. | Schedule-Aware Engine | Target Activity ID(s), Confidence Score, Score breakdown. | Reversible (Matching can be re-run against new baseline). |
| **`VALIDATED`** | Match verified by evidence thresholds or explicit human planner sign-off. | Auto-Pass Rule / Planner Approval | Verifying evidence refs, planner decision log, reasoning trace. | Reversible (Planner can revoke validation if dispute arises). |
| **`PROJECTED`** | Verified event projected as actual start/finish or progress % in schedule view. | Projection Engine Trigger | Approved `TrustedExecutionEvent`, target schedule version. | Reversible (Projections can be rolled back to prior baseline state). |

---

## 2. End-to-End User Journeys

### Journey A: Schedule Import & Activity Fingerprinting Journey
* **Actor:** Senior Planning Engineer (PMO)
* **Goal:** Ingest a Primavera P6 `.xer` baseline schedule manifest and generate multi-vector Activity Fingerprints.
* **Step-by-Step Flow:**
  1. Planner navigates to Schedule Manager and selects "Import Primavera Baseline (.xer / .xml)".
  2. SATYA parses the schedule XML/XER file, extracting project metadata, WBS hierarchy tree, baseline activity rows, CPM dependencies, and planned quantities.
  3. **Validation Check:** SATYA scans for invalid schedule rows (missing Activity IDs, orphaned activities without WBS parent, negative durations). Invalid rows are flagged in an Import Exception Log.
  4. For every valid L5/L6 activity, SATYA derives an **Activity Fingerprint** combining:
     * *Semantic Vector:* Embedded activity name, description, WBS path, and discipline tags.
     * *Structural Context:* Parent WBS node ID, predecessor activity IDs, successor activity IDs.
     * *Spatial Bounds:* Chainage interval $[S_{\text{chain}}, E_{\text{chain}}]$ or location tag.
     * *Temporal Window:* Active execution bounds $[T_{\text{start}} - \Delta t, T_{\text{finish}} + \Delta t]$.
  5. SATYA displays an **Import Summary**: "1,420 L5 activities imported successfully. 1,420 Activity Fingerprints generated. 3 invalid rows flagged."

---

### Journey B: Field Report Ingestion to Trusted Event Journey
* **Actor:** EPC Contractor Engineer / Site Supervisor (Provider) $\rightarrow$ Planner (Validator)
* **Goal:** Transform a multi-tab Excel Daily Progress Report (DPR) into verified schedule actuals.
* **Step-by-Step Flow:**
  1. Contractor uploads `DPR_2026_09_04_Sec2.xlsx` via transmittal interface.
  2. **`OBSERVED`**: System archives original Excel file immutably in raw storage with SHA-256 hash.
  3. **`EXTRACTED`**: Parser reads sheet rows, extracting: Action = `TRENCHING`, Quantity = `180m`, Location = `Km 14.100 to 14.280`, Date = `2026-09-04`, Snippet = `"Completed 180m trenching at Ch 14+100 using 2 excavators"`.
  4. **`MATCHED`**: Matching engine compares extracted event against active Activity Fingerprints. It identifies `ACT-4020: Mainline Trenching - Sec B (Km 10-15)` as candidate match with $\text{Confidence} = 0.92$.
  5. **`VALIDATED`**: Confidence exceeds auto-pass threshold ($\ge 0.85$). Attached site photo photo `IMG_4019.jpg` is auto-verified. Event transitions to `VALIDATED`.
  6. **`PROJECTED`**: SATYA calculates cumulative progress on `ACT-4020` ($Q_{\text{cum}} = 4,200\text{m} / 5,000\text{m} = 84\%$), updates actual start/finish status, and generates candidate Primavera schedule projection.

---

### Journey C: Ambiguous Match Resolution Journey
* **Actor:** Planning Engineer (PMO)
* **Goal:** Resolve a field observation that matches multiple baseline candidate activities.
* **Step-by-Step Flow:**
  1. Field report submitted: `"Welding 14 joints completed at Section B"`.
  2. Matching engine evaluates candidates:
     * Candidate 1: `ACT-3020: Mainline Welding - Sec B (Km 10-15)` ($\text{Confidence} = 0.68$)
     * Candidate 2: `ACT-3040: Tie-In Welding - Sec B (Km 10-15)` ($\text{Confidence} = 0.64$)
  3. Because candidates have close scores and neither exceeds $0.85$, SATYA sets status to `MATCHED (AMBIGUOUS)` and places the event in the **HITL Review Queue**.
  4. Planner opens HITL queue, views raw DPR snippet, location chainage, and candidate breakdown.
  5. Planner clicks "Inspect Evidence", sees that the joint numbers belong to tie-in welds, selects Candidate 2 (`ACT-3040`), and clicks "Confirm Match".
  6. SATYA logs planner override decision in Institutional Memory and updates event status to `VALIDATED`.

---

### Journey D: Unmatched Activity Journey
* **Actor:** Planning Engineer (PMO)
* **Goal:** Safely handle a field observation that cannot be linked to any existing baseline activity.
* **Step-by-Step Flow:**
  1. Field report submitted: `"Constructed temporary bypass culvert near stream Ch 12+800"`.
  2. Matching engine evaluates all baseline Activity Fingerprints. Highest candidate score is $0.22$.
  3. **Rule 5 & Rule 6 Enforcement:** SATYA refuses to invent an Activity ID or assign a low-confidence match. It marks the event as `UNMATCHED` with reasoning trace: `"No baseline activity found matching 'temporary bypass culvert' in WBS Section B"`.
  4. Event is routed to the **Unmatched Observations Queue**.
  5. Planner inspects item: determines whether this is un-scheduled extra work (variations) or requires manual assignment to a contingency WBS package. Planner assigns event or tags as "Out of Scope Variation".

---

### Journey E: Contradictory Report Conflict Journey
* **Actor:** Planning Engineer (PMO) & QA Supervisor
* **Goal:** Detect and resolve opposing progress claims submitted by different field sources.
* **Step-by-Step Flow:**
  1. **Source A (Contractor DPR):** Reports `"Hydrostatic testing of Section 1 pipeline successfully completed on 2026-09-04"`.
  2. **Source B (TPIA Inspection Report):** Uploaded 2 hours later, reports `"Hydrotest failed at 45 bar due to flange gasket leak near Valve Station 2"`.
  3. SATYA's Conflict Engine cross-references both events targeting activity `ACT-8010: Hydrotest Section 1`.
  4. System detects contradiction between `Completed` claim and `QA_Failed` report.
  5. SATYA preserves both events in the ledger, flags `ACT-8010` with **`ConflictFlag: QA_Contradiction`**, and prevents automatic schedule projection.
  6. Item appears in HITL Queue with alert badge: *"Contradictory Claim Detected"*. Planner reviews both documents, confirms QA failure, marks activity as `ON_HOLD / REWORK`, and issues non-conformance ticket.

---

### Journey F: Evidence Gap Detection Journey
* **Actor:** Planning Engineer (PMO)
* **Goal:** Identify active baseline activities on the critical path receiving zero field reporting.
* **Step-by-Step Flow:**
  1. SATYA scans active schedule baseline window $[T_{\text{current}} - 7\text{ days}, T_{\text{current}}]$.
  2. System identifies activity `ACT-5010: Compressor Foundation Concreting` had Planned Start date `2026-08-28` and sits on the Critical Path.
  3. System checks Execution Event Ledger: **Zero execution events** logged for `ACT-5010` in the last 10 days.
  4. **Rule 9 Enforcement:** System DOES NOT mark the activity as "Delayed" or "Not Started" automatically. It classifies `ACT-5010` with status **`EVIDENCE_GAP`**.
  5. Planner dashboard highlights `ACT-5010` under **Evidence Gap Warnings**, allowing the planner to send an automated clarification request to the Site Engineer.

---

### Journey G: Validated Schedule Projection Journey
* **Actor:** Planning Engineer (PMO)
* **Goal:** Project validated execution events into an audit-proof schedule update.
* **Step-by-Step Flow:**
  1. Planner selects "Generate Schedule Projection" for Week 36.
  2. SATYA aggregates all events in state `VALIDATED`.
  3. System calculates updated `Actual Start`, `Actual Finish`, and `Physical % Complete` for all impacted L5 activities.
  4. System generates a **Schedule Projection Transmittal** containing:
     * Comparison Table: Current P6 Baseline vs. SATYA Evidence-Backed Projection.
     * Evidence Audit Index: Clickable links from every proposed % update back to raw DPR text & photo proof.
  5. Planner reviews transmittal, clicks "Export Approved Primavera Update (.xer / .xml)", and updates formal P6 schedule baseline.
