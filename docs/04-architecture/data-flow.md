# System Data Flow & Pipeline Architecture

> **Document Type:** System Data Flow Specification  
> **Governance Status:** Phase 3 Deliverable  
> **Project:** SATYA — Oil India Limited (SIH 2026)  

---

## 1. End-to-End Pipeline Data Flow

The flow of information through SATYA follows a deterministic 7-stage processing pipeline:

```
[FIELD OBSERVATION SOURCE]
   │ (File Upload / API transmittal)
   ▼
[STAGE 1: SOURCE INGESTION & ARCHIVING]
   │  - Stores raw file immutably in storage
   │  - Computes SHA-256 hash & creates SourceDocument record (State: OBSERVED)
   ▼
[STAGE 2: CONTENT NORMALIZATION & FRAGMENTATION]
   │  - Normalizes text encoding & extracts raw fragments
   │  - Attaches machine-resolvable provenance pointers (PDF page, Excel sheet/row, etc.)
   ▼
[STAGE 3: EXECUTION EVENT EXTRACTION]
   │  - Extracts work action, quantity, UOM, chainage, discipline, date
   │  - Emits ExecutionEvent payload (State: EXTRACTED)
   ▼
[STAGE 4: CANDIDATE RETRIEVAL & SCHEDULE-AWARE MATCHING]
   │  - Pre-filters Activity Fingerprints by discipline & temporal window
   │  - Evaluates semantic, structural WBS, and spatial similarity
   │  - Enforces Closed-Vocabulary Guardrail (Rule 5)
   │  - Emits candidate matches + score breakdown (State: MATCHED)
   ▼
[STAGE 5: EVIDENCE VERIFICATION & CONFLICT DETECTION]
   │  - Calculates multi-factor ConfidenceAssessment score ($[0.0, 1.0]$)
   │  - Binds verifying evidence artifacts (photos, QA certificates)
   │  - Cross-references opposing reports for contradictions (State: CONFLICTED if flag)
   ▼
[STAGE 6: HUMAN VALIDATION GATE (HITL)]
   │  - Auto-passes high-confidence verified events ($\ge \theta_{\text{auto}}$)
   │  - Routes low-confidence, ambiguous, or conflicted events to Planner Review Queue
   │  - Captures planner decision & logs to Institutional Memory (State: VALIDATED)
   ▼
[STAGE 7: SCHEDULE PROJECTION & TRANSMITTAL EXPORT]
   │  - Aggregates validated events into physical % complete & actual start/finish
   │  - Renders schedule actuals view & exports Primavera transmittal (.xer / .xml)
   ▼
[SCHEDULE ACTUALS DISPLAY & S-CURVE ROLLUP]
```

---

## 2. Detailed Data Transformation Pipeline

```
RAW FIELD INPUT              EXTRACTED EVENT             CANDIDATE MATCH             TRUSTED EVENT
+-------------------+        +-------------------+       +-------------------+       +-------------------+
| Excel DPR Sheet   |        | ExecutionEvent    |       | CandidateMatch    |       | TrustedEvent      |
| Row 42:           |        | Action: TRENCHING |       | ActivityID:       |       | State: VALIDATED  |
| "180m trenching   | ====>  | Qty: 180.0        | ====> | ACT-4020          | ====> | ApprovedBy:       |
| dug at Ch 14+100" |        | UOM: Meters       |       | Confidence: 0.92  |       | Planner_01        |
| Timestamp: Sep 4  |        | Provenance:       |       | Status: MATCHED   |       | Primavera Update: |
+-------------------+        | Sheet2!Row42      |       +-------------------+       | P6 Actual = 84%   |
                             +-------------------+                                   +-------------------+
```

---

## 3. Reversibility & Auditability Mechanics

* **State Reversibility:** If a planner realizes an approved match was based on faulty contractor data, the event state can be transitioned from `VALIDATED` back to `REJECTED` or `AMBIGUOUS`.
* **Audit Trail Preservation:** Reversing a state transition **does not delete** the previous `VALIDATED` event record. Instead, a new `ValidationDecision` entry is appended to the ledger with decision type `REVOKED`, preserving the full audit trail.
