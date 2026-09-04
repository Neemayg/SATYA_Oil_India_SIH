# Architectural Decision Records (ADR)

> **Document Type:** Architectural Decision Log  
> **Project:** SATYA — Oil India Limited (SIH 2026)  
> **Status:** Canonical Record  

---

## Decision Index

| ID | Title | Date | Status |
| :--- | :--- | :--- | :--- |
| [DEC-001](#dec-001-execution-truth-layer-as-central-product-architecture) | Execution Truth Layer as Central Product Architecture | 2026-09-04 | APPROVED |
| [DEC-002](#dec-002-execution-events-treated-as-immutable-observations) | Execution Events Treated as Immutable Observations | 2026-09-04 | APPROVED |
| [DEC-003](#dec-003-ai-cannot-invent-schedule-activities) | AI Cannot Invent Schedule Activities | 2026-09-04 | APPROVED |
| [DEC-004](#dec-004-human-validation-gate-for-uncertain-ai-interpretation) | Human Validation Gate for Uncertain AI Interpretation | 2026-09-04 | APPROVED |

---

### DEC-001: Execution Truth Layer as Central Product Architecture

* **ID:** DEC-001
* **Date:** 2026-09-04
* **Decision:** Establish an Execution Truth Layer (ETL) as the core system architecture between raw field inputs and schedule actuals.
* **Context:** Upstream oil and gas projects suffer from a disconnect between field execution reality (unstructured DPRs, site notes) and Primavera P6 L5/L6 project schedules. Standard project tools try to force field engineers to enter Primavera activity IDs directly, leading to low adoption, or rely on unverified manual spreadsheet summaries.
* **Options Considered:**
  1. *Direct User Data Entry into PMIS:* Require field staff to manually tag Primavera Activity IDs in site logs. (Rejected: Unrealistic for remote field contractors).
  2. *Generic Conversational AI Chatbot:* Build a query-answering bot on top of DPR documents. (Rejected: Provides summaries but fails to produce structured, audit-ready schedule actuals).
  3. *Execution Truth Layer Architecture:* Build an automated intelligence layer that ingests raw field inputs, extracts structured Execution Events, matches them against Activity Fingerprints, and verifies evidence before updating progress. (Chosen).
* **Decision Made:** Option 3 — Build the Execution Truth Layer.
* **Reason:** Guarantees schedule grounding, preserves raw evidence provenance, and bridges the operational gap between field reality and formal scheduling.
* **Consequences:** The system must implement dedicated event extraction, fingerprinting, matching, and conflict verification pipelines.
* **Status:** APPROVED

---

### DEC-002: Execution Events Treated as Immutable Observations

* **ID:** DEC-002
* **Date:** 2026-09-04
* **Decision:** Treat all extracted execution events and raw field inputs as immutable, append-only records.
* **Context:** Progress reports in construction projects are frequently disputed during audit or contract billing. Modifying or overwriting past progress entries destroys the audit trail.
* **Options Considered:**
  1. *Mutable State Database:* Update field progress rows in-place when new reports arrive. (Rejected: Destroys historical auditability and provenance).
  2. *Immutable Observation Ledger:* Store every field report as an immutable `ExecutionEvent` with full provenance, treating progress calculation as a deterministic projection over the ledger. (Chosen).
* **Decision Made:** Option 2 — Immutable Event Ledger.
* **Reason:** Ensures 100% auditability, supports retrospective analysis, and enables re-running matching models as institutional memory improves.
* **Consequences:** Database storage must be designed for append-only events. Corrections are logged as new compensating events or planner overrides rather than in-place edits.
* **Status:** APPROVED

---

### DEC-003: AI Cannot Invent Schedule Activities

* **ID:** DEC-003
* **Date:** 2026-09-04
* **Decision:** Enforce a strict constraint preventing AI models from inventing or generating schedule Activity IDs or WBS IDs.
* **Context:** Large Language Models are prone to hallucination when generating structured identifiers, which can corrupt the PMIS schedule baseline.
* **Options Considered:**
  1. *Unconstrained LLM Generation:* Allow LLM to output freeform activity IDs based on prompt context. (Rejected: High risk of hallucinated IDs).
  2. *Strict Closed-Vocabulary Constrained Matching:* Force matching outputs to strictly map to valid candidate Activity IDs provided from the ingested baseline manifest, or return `UNMATCHED`. (Chosen).
* **Decision Made:** Option 2 — Strict constrained matching with `UNMATCHED` support.
* **Reason:** Ensures data integrity and prevents corrupt schedule updates.
* **Consequences:** Matching algorithms must validate generated candidate IDs against the ingested baseline dictionary before accepting any match result.
* **Status:** APPROVED

---

### DEC-004: Human Validation Gate for Uncertain AI Interpretation

* **ID:** DEC-004
* **Date:** 2026-09-04
* **Decision:** Position Human-in-the-Loop (HITL) planner validation between uncertain AI matching interpretations and trusted actual schedule updates.
* **Context:** Fully automated schedule updates based on probabilistic matching can introduce false progress entries, leading to incorrect critical path calculations.
* **Options Considered:**
  1. *Fully Autonomous Schedule Auto-Update:* Automatically update Primavera schedules whenever a match is made. (Rejected: Dangerous for high-value projects).
  2. *Threshold-Gated Human Validation (HITL):* Automatically accept high-confidence matches ($\ge \theta_{\text{auto}}$), while routing low-confidence or conflicting matches to a planner review queue. (Chosen).
* **Decision Made:** Option 2 — Threshold-gated HITL validation.
* **Reason:** Balances automation efficiency with human planner accountability and risk control.
* **Consequences:** The application requires a dedicated Human Validation UI and queue workflow. Planner feedback is saved to Institutional Memory.
* **Status:** APPROVED
