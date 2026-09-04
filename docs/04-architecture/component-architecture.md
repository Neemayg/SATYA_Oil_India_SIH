# Component Architecture Specifications

> **Document Type:** System Component Architecture Specification  
> **Governance Status:** Phase 3 Deliverable  
> **Project:** SATYA — Oil India Limited (SIH 2026)  

---

## 1. Modular Component Overview

SATYA is structured into 17 discrete, loosely-coupled conceptual components grouped into 5 functional subsystems:

```
+-----------------------------------------------------------------------------------+
| 1. SCHEDULE & FINGERPRINTING SUBSYSTEM                                           |
|    - C1: Schedule Ingestion Layer       - C2: Schedule Normalization Layer        |
|    - C3: Activity Fingerprint Engine                                              |
+-----------------------------------------------------------------------------------+
| 2. SOURCE INGESTION & EXTRACTION SUBSYSTEM                                       |
|    - C4: Source Ingestion Layer         - C5: Content Normalization Layer         |
|    - C6: Event Extraction Pipeline Layer                                          |
+-----------------------------------------------------------------------------------+
| 3. MATCHING & RECONCILIATION SUBSYSTEM                                           |
|    - C7: Candidate Retrieval Layer      - C8: Schedule-Aware Matching Engine      |
|    - C9: Evidence & Provenance Engine   - C10: Confidence Engine                |
|    - C11: Conflict Detection Engine                                               |
+-----------------------------------------------------------------------------------+
| 4. VALIDATION & LEDGER SUBSYSTEM                                                 |
|    - C12: Human Validation Layer (HITL) - C13: Execution Truth Ledger             |
|    - C14: Schedule Projection Layer                                               |
+-----------------------------------------------------------------------------------+
| 5. INTELLIGENCE & GOVERNANCE SUBSYSTEM                                           |
|    - C15: Institutional Memory Layer    - C16: Audit Layer                        |
|    - C17: Analytics & Reporting Layer                                             |
+-----------------------------------------------------------------------------------+
```

---

## 2. Component Specifications

### C1: Schedule Ingestion Layer
* **Purpose:** Ingests raw Primavera P6 (`.xer`, `.xml`) or MS Project (`.xml`) schedule export files.
* **Inputs:** Raw schedule export byte streams or transmittal files.
* **Outputs:** Raw schedule document artifact stored in storage with hash.
* **Responsibilities:** Validates file encoding, verifies schema syntax, archives raw file.

### C2: Schedule Normalization Layer
* **Purpose:** Parses raw schedule files into a normalized internal schedule graph representation.
* **Inputs:** Raw schedule file artifact.
* **Outputs:** `NormalizedSchedule` manifest (WBS nodes, activity entities, CPM ties).
* **Responsibilities:** Extracts activity attributes, builds parent-child WBS tree, flags malformed rows in Exception Log.

### C3: Activity Fingerprint Engine
* **Purpose:** Generates multi-vector Activity Fingerprints for every normalized baseline activity.
* **Inputs:** `NormalizedSchedule` manifest.
* **Outputs:** Cached `ActivityFingerprint` records.
* **Responsibilities:** Computes semantic vector embeddings, extracts structural topology, bounds spatial chainages, bounds temporal execution windows.

### C4: Source Ingestion Layer
* **Purpose:** Receives heterogeneous field observation inputs (DPRs, text notes, voice transcript payloads, photos).
* **Inputs:** Raw field files or API transmittal payloads.
* **Outputs:** Immutable `SourceDocument` record in `OBSERVED` state.
* **Responsibilities:** Generates unique source ID, computes SHA-256 hash, extracts document metadata (author, timestamp, origin).

### C5: Content Normalization Layer
* **Purpose:** Converts multi-format source content into standard machine-readable text fragments with provenance markers.
* **Inputs:** `SourceDocument`.
* **Outputs:** Array of `SourceFragment` objects (text blocks, table rows, transcript spans).
* **Responsibilities:** Normalizes character encoding, strips formatting noise, attaches machine-resolvable provenance pointers.

### C6: Execution Event Extraction Pipeline Layer
* **Purpose:** Extracts structured, atomic work execution actions from normalized content fragments.
* **Inputs:** `SourceFragment` records.
* **Outputs:** Normalized `ExecutionEvent` objects in `EXTRACTED` state.
* **Responsibilities:** Parses action verbs, quantities, units of measure, site locations/chainages, disciplines, and dates.

### C7: Candidate Retrieval Layer
* **Purpose:** Performs fast pre-filtering to retrieve plausible candidate Activity Fingerprints for an extracted event.
* **Inputs:** `ExecutionEvent`.
* **Outputs:** Ranked candidate Activity IDs ($N \le 10$).
* **Responsibilities:** Filters by discipline, temporal execution window, and WBS path to narrow the search space before deep matching.

### C8: Schedule-Aware Matching Engine
* **Purpose:** Executes multi-layered evaluation of candidate activities against event payload.
* **Inputs:** `ExecutionEvent` + Candidate Fingerprints.
* **Outputs:** Ranked candidate match list with factor breakdown and match outcome classification (`MATCHED`, `AMBIGUOUS`, `UNMATCHED`, `CONFLICTED`).
* **Responsibilities:** Calculates semantic similarity, verifies structural WBS logic, checks temporal bounds, enforces Closed-Vocabulary Guardrail (Rule 5).

### C9: Evidence & Provenance Engine
* **Purpose:** Links execution events to supporting physical/documentary evidence and machine-resolvable provenance locators.
* **Inputs:** `ExecutionEvent` + Source Artifacts.
* **Outputs:** `ProvenanceRecord` and `EvidenceLink` objects.
* **Responsibilities:** Binds events to source locators (PDF page/region, Excel sheet/row/col, text span, image reference); answers the 8 audit questions (`REQ-EVI-001`).

### C10: Confidence Engine
* **Purpose:** Calculates multi-factor normalized confidence scores ($[0.0, 1.0]$) for candidate matches.
* **Inputs:** Candidate matches, evidence references, historical patterns.
* **Outputs:** Structured `ConfidenceAssessment` object.
* **Responsibilities:** Evaluates identifier agreement, semantic score, spatial alignment, discipline check, and temporal consistency.

### C11: Conflict Detection Engine
* **Purpose:** Detects opposing field progress claims, QA test failures, and out-of-sequence execution logic.
* **Inputs:** Event ledger records targeting the same activity/window.
* **Outputs:** `ConflictFlag` records (`QA_Contradiction`, `Quantity_Discrepancy`, `Out_of_Sequence`).
* **Responsibilities:** Cross-references contractor claims against QA/TPIA certificates; flags contradictions for human review.

### C12: Human Validation Layer (HITL)
* **Purpose:** Manages the review queue and interactive interface for human planner validation.
* **Inputs:** Low-confidence events, ambiguous matches, conflict flags, unmatched events.
* **Outputs:** `ValidationDecision` log (Confirm / Re-map / Reject / Override).
* **Responsibilities:** Presents evidence context to planner; captures human decisions and reason codes; updates event state to `VALIDATED`.

### C13: Execution Truth Ledger
* **Purpose:** Provides durable, append-only storage for all execution events and their validation states.
* **Inputs:** `ExecutionEvent` state updates.
* **Outputs:** Immutable event ledger history.
* **Responsibilities:** Enforces append-only storage; prevents deletion/mutation of historical observations; maintains version links.

### C14: Schedule Projection Layer
* **Purpose:** Projects trusted execution events into schedule actual start/finish dates, physical % complete, and Primavera update exports.
* **Inputs:** `TrustedExecutionEvent` records.
* **Outputs:** Schedule projection view & candidate `.xer`/`.xml` transmittal.
* **Responsibilities:** Aggregates cumulative quantities, calculates actual progress, generates Primavera transmittal without mutating baseline files.

### C15: Institutional Memory Layer
* **Purpose:** Stores validated historical metrics, terminology aliases, and planner corrections.
* **Inputs:** Approved `ValidationDecision` logs & actual task execution durations.
* **Outputs:** Expanded terminology alias dictionary & historical productivity factors.
* **Responsibilities:** Updates alias lookup tables to improve future matching accuracy; feeds empirical duration distributions to planning tools.

### C16: Audit Layer
* **Purpose:** Provides complete system auditability across all operations.
* **Inputs:** Ledger events, validation decisions, system logs.
* **Outputs:** Cryptographically verifiable audit trails.
* **Responsibilities:** Logs user access, system state transitions, and data transmittals.

### C17: Analytics & Reporting Layer
* **Purpose:** Generates executive dashboards, S-curves, evidence-gap alerts, and portfolio health metrics.
* **Inputs:** Schedule projection views & Institutional Memory.
* **Outputs:** Executive dashboards, S-curves, Evidence Gap reports.
* **Responsibilities:** Renders S-curves, surfaces active critical path evidence gaps, displays portfolio status.
