# Functional & Product Requirements Catalogue

> **Document Type:** System Requirements Specification (SRS)  
> **Governance Status:** Phase 2 Deliverable  
> **Project:** SATYA — Oil India Limited (SIH 2026)  

---

## 1. Traceability Matrix Framework

Every requirement in this catalogue traces directly from the SIH Problem Statement and Phase 1 Domain Analysis:

```
[SIH Problem Statement] ──> [Domain Pain Point] ──> [Product Requirement] ──> [Future Test Case]
```

---

## 2. Requirements Catalogue by Category

### Category A: Schedule Management

#### `REQ-SCH-001`: Baseline Schedule Ingestion & Parsing
* **Title:** Ingest Primavera P6 and MS Project Schedule Files
* **Description:** System must import Primavera P6 (`.xer`, `.xml`) and MS Project (`.xml`) baseline schedule manifests, extracting WBS tree nodes, activity attributes, CPM logic ties, and planned quantities.
* **Priority:** `MUST` | **Classification:** `MVP`
* **Actor:** Planning Engineer (PMO)
* **Inputs:** Baseline schedule export file (`.xer`, `.xml`).
* **Outputs:** Parsed schedule manifest object and WBS hierarchy tree.
* **Acceptance Criteria:** Successfully parses 1,000+ L5/L6 activities with zero corruption of WBS relationships or CPM logic ties.
* **Dependencies:** None.

#### `REQ-SCH-002`: Activity Fingerprint Generation
* **Title:** Derive Multi-Vector Activity Fingerprints
* **Description:** System must derive a multi-dimensional Activity Fingerprint for every valid L5/L6 activity combining semantic vector embeddings, WBS structural paths, spatial chainage bounds, and temporal execution windows.
* **Priority:** `MUST` | **Classification:** `MVP`
* **Actor:** Automated System
* **Inputs:** Parsed baseline schedule manifest.
* **Outputs:** Cached `ActivityFingerprint` records for all activities.
* **Acceptance Criteria:** 100% of valid L5/L6 schedule activities have generated fingerprints.
* **Dependencies:** `REQ-SCH-001`.

---

### Category B: Source Ingestion

#### `REQ-ING-001`: Heterogeneous Field Observation Ingestion
* **Title:** Support Multi-Format Field Report Ingestion
* **Description:** System must ingest multi-format field execution observations (Daily Progress Reports in PDF/Excel, digital site notes, voice transcripts, inspection reports).
* **Priority:** `MUST` | **Classification:** `MVP`
* **Actor:** Site Engineer / EPC Contractor
* **Inputs:** Raw report files, text payloads, voice transcript payloads.
* **Outputs:** Raw file artifact stored in `OBSERVED` state with SHA-256 hash.
* **Acceptance Criteria:** Stores original file immutably; emits raw ingestion log entry.
* **Dependencies:** None.

---

### Category C: Execution Event Extraction

#### `REQ-EXT-001`: Entity Extraction & Event Creation
* **Title:** Extract Structured Execution Events from Field Inputs
* **Description:** System must parse raw field inputs to extract action verbs, quantities, units of measure, site locations/chainages, disciplines, and dates into normalized `ExecutionEvent` records.
* **Priority:** `MUST` | **Classification:** `MVP`
* **Actor:** Extractor Engine
* **Inputs:** Raw input artifact from `REQ-ING-001`.
* **Outputs:** Structured `ExecutionEvent` in `EXTRACTED` state.
* **Acceptance Criteria:** Extracted event preserves exact raw text snippet, byte offset, line number, and author metadata (provenance).
* **Dependencies:** `REQ-ING-001`.

---

### Category D: Activity Matching

#### `REQ-MAT-001`: Schedule-Aware Candidate Matching Engine
* **Title:** Match Execution Events to Baseline Activity Fingerprints
* **Description:** System must match candidate `ExecutionEvents` against Activity Fingerprints using semantic similarity, structural WBS context, spatial chainage alignment, and temporal window checks.
* **Priority:** `MUST` | **Classification:** `MVP`
* **Actor:** Matching Engine
* **Inputs:** `ExecutionEvent` + Schedule Baseline Fingerprints.
* **Outputs:** Candidate matches with normalized confidence score ($[0.0, 1.0]$) and factor breakdown.
* **Acceptance Criteria:** Matching engine explicitly returns 1 of 4 formal statuses: `MATCHED`, `AMBIGUOUS`, `UNMATCHED`, or `CONFLICTED`.
* **Dependencies:** `REQ-SCH-002`, `REQ-EXT-001`.

#### `REQ-MAT-002`: Strict AI Guardrail — No Hallucinated Activity IDs
* **Title:** Enforce Closed-Vocabulary Matching (Rule 5)
* **Description:** AI matching engine must NEVER generate or output an Activity ID or WBS ID that does not exist in the ingested baseline schedule manifest.
* **Priority:** `MUST` | **Classification:** `MVP`
* **Actor:** Matching Engine Guardrail
* **Inputs:** Match candidate outputs.
* **Outputs:** Validated match output or forced `UNMATCHED` status.
* **Acceptance Criteria:** Zero invalid or hallucinated Activity IDs accepted into matching outputs under any test scenario.
* **Dependencies:** `REQ-MAT-001`.

---

### Category E: Evidence & Provenance (Core Product Requirement)

#### `REQ-EVI-001`: 8-Question Evidence-Backed Execution Principle
* **Title:** Maintain Full Audit Evidence for Every Execution Event
* **Description:** Every trusted execution event must answer 8 explicit audit questions:
  1. **WHAT** physical work happened?
  2. **WHEN** did it happen?
  3. **WHICH** schedule activity does it correspond to?
  4. **WHY** does SATYA believe this linkage?
  5. **WHAT** evidence artifacts support it?
  6. **WHERE** did the raw data originate (file offset/snippet)?
  7. **WHO / WHAT** validated the event?
  8. **WERE** there conflicting field claims?
* **Priority:** `MUST` | **Classification:** `MVP`
* **Actor:** Evidence Engine
* **Inputs:** Validated Execution Event.
* **Outputs:** Audit-proof Evidence Record.
* **Acceptance Criteria:** 1-click drilldown in UI from schedule update back to raw document line and attached photo proof.
* **Dependencies:** `REQ-EXT-001`, `REQ-MAT-001`.

---

### Category F: Confidence & Validation

#### `REQ-VAL-001`: Threshold-Gated Human-in-the-Loop Workflow
* **Title:** Route Low-Confidence and Disputed Matches to Planner Queue
* **Description:** Events exceeding auto-pass threshold ($\text{Confidence} \ge \theta_{\text{auto}}$) with valid evidence auto-pass to `VALIDATED`. Events with medium/low confidence ($\text{Confidence} < \theta_{\text{auto}}$) or conflict flags are routed to the HITL Planner Queue.
* **Priority:** `MUST` | **Classification:** `MVP`
* **Actor:** Planning Engineer (PMO)
* **Inputs:** Match results and confidence scores.
* **Outputs:** Planner decision log (Confirm / Re-map / Reject).
* **Acceptance Criteria:** Planner review UI presents raw text snippet, candidate ranking, confidence breakdown, and attached evidence.
* **Dependencies:** `REQ-MAT-001`, `REQ-EVI-001`.

---

### Category G: Conflict Detection

#### `REQ-CNF-001`: Multi-Source Contradiction Surface Engine
* **Title:** Detect Opposing Field Progress Claims (Rule 8)
* **Description:** System must detect contradictions between opposing field reports (e.g., Contractor DPR claims 100% complete vs. QA report notes test failure) for the same execution window/activity.
* **Priority:** `MUST` | **Classification:** `MVP`
* **Actor:** Conflict Engine
* **Inputs:** Multiple Execution Events targeting same activity.
* **Outputs:** `ConflictFlag: QA_Contradiction` or `Quantity_Discrepancy`.
* **Acceptance Criteria:** System preserves both events, prevents automatic projection, and alerts planner in HITL queue.
* **Dependencies:** `REQ-EXT-001`, `REQ-MAT-001`.

---

### Category H: Unmatched / New Activity Handling

#### `REQ-UNM-001`: Unmatched Field Observation Management (Rule 6)
* **Title:** Preserve and Classify Unmatched Field Observations
* **Description:** Field observations that cannot be matched to baseline activities with confidence must be classified as `UNMATCHED`, preserved with provenance, and routed to the Unmatched Queue.
* **Priority:** `MUST` | **Classification:** `MVP`
* **Actor:** Planning Engineer (PMO)
* **Inputs:** `UNMATCHED` execution events.
* **Outputs:** Planner classification (Assign to Contingency WBS / Tag as Scope Variation / Dismiss).
* **Acceptance Criteria:** Zero unmatched events discarded silently.
* **Dependencies:** `REQ-MAT-001`.

---

### Category I: Evidence Gap Detection

#### `REQ-GAP-001`: Active Critical Path Evidence Gap Identification (Rule 9)
* **Title:** Detect Unreported Active Schedule Activities
* **Description:** System must scan active schedule windows to identify tasks on the critical path receiving zero field execution events.
* **Priority:** `MUST` | **Classification:** `MVP`
* **Actor:** Time Monitoring Engine
* **Inputs:** Baseline Schedule + Event Ledger.
* **Outputs:** `EVIDENCE_GAP` warning badges.
* **Acceptance Criteria:** System classifies missing data as `EVIDENCE_GAP` and DOES NOT automatically mark tasks as "Delayed" or "Not Started".
* **Dependencies:** `REQ-SCH-001`, `REQ-EXT-001`.

---

### Category J: Schedule Projection

#### `REQ-PRJ-001`: Audit-Proof Actual Schedule Projection
* **Title:** Project Verified Events to Schedule Actuals
* **Description:** System must aggregate `VALIDATED` events to compute actual start/finish dates, physical % complete, and schedule variance without corrupting original baseline files.
* **Priority:** `MUST` | **Classification:** `MVP`
* **Actor:** Projection Engine
* **Inputs:** Approved `TrustedExecutionEvent` records.
* **Outputs:** Updated Primavera schedule view & `.xer` transmittal file.
* **Acceptance Criteria:** Emits candidate P6 update transmittal backed 100% by evidence audit index.
* **Dependencies:** `REQ-VAL-001`.

---

### Category K: Institutional Memory

#### `REQ-MEM-001`: Historical Execution Intelligence Store
* **Title:** Accumulate Planner Overrides & Actual Productivity Rates
* **Description:** System must store planner HITL corrections, terminology aliases, and actual task durations to refine future activity matching and baseline estimation.
* **Priority:** `MUST` | **Classification:** `MVP`
* **Actor:** Institutional Memory Store
* **Inputs:** Approved HITL decisions & validated actual durations.
* **Outputs:** Expanded alias dictionary & productivity benchmarks.
* **Acceptance Criteria:** Saved terminology aliases automatically boost confidence scores on future matching runs.
* **Dependencies:** `REQ-VAL-001`.

---

### Category L & M: Audit & Analytics

#### `REQ-AUD-001`: Immutable Ledger Auditability (Rule 2 & 3)
* **Title:** Maintain Read-Only Immutable Execution Event Ledger
* **Description:** All raw field inputs and extracted events must be stored in an append-only ledger with SHA-256 checksums and immutable provenance records.
* **Priority:** `MUST` | **Classification:** `MVP`
* **Actor:** Ledger Engine
* **Acceptance Criteria:** Zero data modification or deletion allowed on historical ledger records.

---

## 3. Product Boundaries: What SATYA Owns vs. Does NOT Own

| SATYA OWNS | SATYA DOES NOT OWN |
| :--- | :--- |
| Ingestion & entity extraction of field observations | Official enterprise project schedule database (Primavera P6 server) |
| Execution Event Ledger & provenance archiving | Contractual billing approval or financial accounting ledger |
| Activity Fingerprint derivation & matching engine | Physical site safety enforcement or site security |
| Multi-modal evidence verification & confidence math | Real-time IoT sensor network maintenance |
| Conflict detection & Evidence Gap flagging | Autonomous project re-baselining without planner consent |
| HITL Validation workflow interface | Unquestioned AI authority over human planners |

---

## 4. Product Success Metrics

| Metric Name | What It Measures | Target MVP Threshold | Why It Matters |
| :--- | :--- | :--- | :--- |
| **Matching Precision** | % of auto-passed matches ($\text{Conf} \ge 0.85$) verified correct by planner. | $\ge 90\%$ | Ensures automated matching does not introduce false progress. |
| **False-Match Rate** | % of events incorrectly linked to wrong Activity ID. | $\le 2.0\%$ | Prevents schedule baseline corruption. |
| **Unmatched Detection Quality** | % of ambiguous/invalid events correctly classified as `UNMATCHED`. | $100\%$ | Enforces Rule 6 & prevents AI hallucination. |
| **Conflict Surface Recall** | % of simulated contradictory reports successfully flagged. | $100\%$ | Prevents hidden contractor vs. QA disputes. |
| **Planner Efficiency Gain** | Reduction in manual planner time required to process DPR updates. | $\ge 60\%$ reduction | Primary ROI for Oil India PMO team. |
| **Provenance Completeness** | % of trusted events with 100% traceable source snippet and offset. | $100\%$ | Ensures 100% auditability for CAG/internal audits. |

---

## 5. SIH Demo Script (15-Step Proof Sequence)

The eventual hackathon demonstration will execute the following 15-step sequence:
1. Import sample Oil India Primavera P6 baseline schedule (`.xer`).
2. Display baseline schedule tree with 100+ L5/L6 activities.
3. Ingest heterogeneous field inputs (Excel DPR, PDF report, site voice transcript, photo).
4. Run Execution Event extraction pipeline.
5. Display extracted `ExecutionEvent` ledger entries with raw text snippets and file offsets.
6. Run Schedule-Aware Matching Engine against Activity Fingerprints.
7. Show high-confidence match ($\text{Confidence} = 0.94$) auto-passing to `VALIDATED`.
8. Show attached geotagged photo proof supporting the high-confidence match.
9. Demonstrate an **Ambiguous Match** ($\text{Confidence} = 0.65$) routed to HITL queue.
10. Demonstrate an **Unmatched Event** ("Constructed temporary bypass culvert") safely classified as `UNMATCHED`.
11. Demonstrate a **Contradictory Report** (Contractor 100% complete vs. QA test failure) flagged with alert badge.
12. Perform 1-click planner validation resolving the ambiguous match in the HITL interface.
13. Show creation of immutable `TrustedExecutionEvent`.
14. Project validated actuals into Primavera schedule view (S-curve update).
15. Show how planner correction was saved to **Institutional Memory** to expand terminology aliases.
