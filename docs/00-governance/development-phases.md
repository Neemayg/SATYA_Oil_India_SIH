# Development Phases & Lifecycle Control

> **Governance Standard:** Development Phase Gate Controls  
> **Project:** SATYA — Oil India Limited (SIH 2026)  
> **Current Phase:** `PHASE 0 - Foundation`  

---

## Lifecycle Overview

The SATYA project strictly adheres to a sequential 17-phase implementation lifecycle. No implementation work (coding, package installation, database setup) may proceed outside the currently active phase.

---

## Phase Definitions

### PHASE 0: Foundation

* **Purpose:** Establish project governance, agent instructions, canonical context, non-negotiable rules, architectural decisions (ADRs), assumptions register, glossary, and documentation skeleton.
* **Inputs:** SIH 2026 problem statement and Oil India Limited domain context.
* **Expected Outputs:** `AGENTS.md`, `README.md`, `CHANGELOG.md`, directory skeleton, and complete `docs/00-governance/` directory artifacts.
* **Dependencies:** None.
* **Exit Criteria:** All governance documents created, 20 non-negotiable rules established, zero application code created, directory skeleton in place.

---

### PHASE 1: Problem + Domain Understanding

* **Purpose:** Deeply document the Oil India Limited execution domain, Primavera P6 L1-L6 schedule structures, DPR formats, and physical oil/gas construction workflows.
* **Inputs:** `docs/00-governance/context.md`, domain documentation, and sample oil/gas pipeline/drilling project schedules.
* **Expected Outputs:** Comprehensive documentation in `docs/01-problem/` and `docs/03-domain/`.
* **Dependencies:** PHASE 0.
* **Exit Criteria:** Complete mapping of Oil India field terminology, DPR formats, Primavera schedule attributes, and failure modes approved by domain context.

---

### PHASE 2: Product + Requirements

* **Purpose:** Define explicit functional requirements, non-functional requirements, user personas, MVP boundary scope, and acceptance criteria.
* **Inputs:** `docs/01-problem/` and `docs/03-domain/`.
* **Expected Outputs:** PRD, user stories, and acceptance criteria documents in `docs/02-product/`.
* **Dependencies:** PHASE 1.
* **Exit Criteria:** PRD completed with unambiguous MVP feature boundaries, explicit exclusion list, and signed-off exit criteria.

---

### PHASE 3: Architecture + Data Model

* **Purpose:** Design detailed system component architecture, data flow diagrams, database schemas, and canonical event models.
* **Inputs:** `docs/02-product/` and `docs/00-governance/decisions.md`.
* **Expected Outputs:** Architecture specifications in `docs/04-architecture/` and data model definitions in `docs/06-data/`.
* **Dependencies:** PHASE 2.
* **Exit Criteria:** Complete JSON/SQL schemas for `ExecutionEvent`, `ActivityFingerprint`, `MatchResult`, `ConflictFlag`, and `InstitutionalMemory` documented.

---

### PHASE 4: Synthetic Data

* **Purpose:** Specify and generate realistic synthetic test datasets (Primavera P6 schedules, DPR documents, site logs, voice transcripts, inspection reports).
* **Inputs:** `docs/06-data/` schemas and `docs/03-domain/` taxonomy.
* **Expected Outputs:** Synthetic schedule files in `data/synthetic/` and generation scripts in `scripts/`.
* **Dependencies:** PHASE 3.
* **Exit Criteria:** At least 2 complete, realistic Oil India project schedules (L5/L6) and 50+ corresponding multi-format field observations generated and validated against schemas.

---

### PHASE 5: Execution Event Pipeline

* **Purpose:** Implement the raw field input ingestion engine and entity extraction pipeline to convert field text/files into structured `ExecutionEvent` records.
* **Inputs:** `data/synthetic/` observations and `docs/06-data/` event schemas.
* **Expected Outputs:** Ingestion module in `backend/` or `ai/` producing validated `ExecutionEvent` records with 100% provenance tracking.
* **Dependencies:** PHASE 4.
* **Exit Criteria:** Execution event parser successfully converts raw DPRs/memos into valid schema-conforming `ExecutionEvent` records preserving complete raw provenance.

---

### PHASE 6: Activity Fingerprinting

* **Purpose:** Implement the generator that computes multi-dimensional `ActivityFingerprints` (semantic, structural WBS, temporal window, physical zone) for baseline schedule activities.
* **Inputs:** Synthetic Primavera schedule files (`data/synthetic/`).
* **Expected Outputs:** Fingerprinting engine in `ai/` or `backend/` creating cached `ActivityFingerprint` records.
* **Dependencies:** PHASE 5.
* **Exit Criteria:** 100% of schedule activities in test baseline converted to structured, searchable Activity Fingerprints with semantic embeddings and WBS topological context.

---

### PHASE 7: Schedule-Aware Matching Engine

* **Purpose:** Build the core engine that matches candidate `ExecutionEvents` against `ActivityFingerprints` using semantic + structural + temporal logic.
* **Inputs:** `ExecutionEvents` (Phase 5) and `ActivityFingerprints` (Phase 6).
* **Expected Outputs:** Matching engine module returning candidate activity matches or explicit `UNMATCHED` status.
* **Dependencies:** PHASE 6.
* **Exit Criteria:** Engine evaluates test event inputs, correctly returns matches or `UNMATCHED`, and adheres to Rule 5 (no hallucinated activity IDs).

---

### PHASE 8: Evidence + Confidence + Conflict Engine

* **Purpose:** Implement multi-factor confidence scoring ($[0.0, 1.0]$), multi-modal evidence verification, contradictory observation surfacing, and evidence-gap detection.
* **Inputs:** Match candidates from Phase 7 and raw evidence attachments.
* **Expected Outputs:** Scoring and conflict detection module outputting `ConfidenceScore`, `EvidenceVerification`, and `ConflictFlags`.
* **Dependencies:** PHASE 7.
* **Exit Criteria:** Engine correctly flags simulated contradictory DPR claims and identifies un-reported active schedule tasks in test datasets.

---

### PHASE 9: Human Validation (HITL) Workflow

* **Purpose:** Implement the backend logic and queue management for Human-in-the-Loop planner review of low-confidence or disputed matches.
* **Inputs:** Flagged matches and conflicts from Phase 8.
* **Expected Outputs:** HITL verification API and queue manager in `backend/`.
* **Dependencies:** PHASE 8.
* **Exit Criteria:** Low-confidence matches ($\text{Confidence} < \theta$) are cleanly placed in review queue; planner decisions (confirm/re-map/reject) update match status.

---

### PHASE 10: Actual Progress + Schedule Projection Engine

* **Purpose:** Build the deterministic engine that aggregates verified Execution Events to calculate actual start/finish dates, physical % complete, and schedule variance projections.
* **Inputs:** Verified Execution Events from Phase 9 / Phase 8.
* **Expected Outputs:** Progress calculation and baseline variance projection module.
* **Dependencies:** PHASE 9.
* **Exit Criteria:** Produces trusted actual progress metrics without directly corrupting baseline schedule files without explicit validation.

---

### PHASE 11: Backend Application Services

* **Purpose:** Package execution event pipelines, matching engines, scoring modules, and progress projectors into clean, documented REST/gRPC backend services.
* **Inputs:** Modules from Phase 5 through Phase 10.
* **Expected Outputs:** Runnable backend service codebase in `backend/`.
* **Dependencies:** PHASE 10.
* **Exit Criteria:** Backend API endpoints operational, fully tested with unit/integration tests, and documented in `docs/08-api/`.

---

### PHASE 12: Frontend Planner Dashboard & HITL Interface

* **Purpose:** Develop the user-facing web interface for project planners and managers (Schedule View, Event Ledger, HITL Validation Interface, Evidence Inspector).
* **Inputs:** Backend APIs (Phase 11) and UX specs (`docs/09-frontend/`).
* **Expected Outputs:** Modern, responsive web application in `frontend/`.
* **Dependencies:** PHASE 11.
* **Exit Criteria:** Interactive dashboard allows planners to inspect schedule activities, review evidence, resolve low-confidence matches, and view verified progress.

---

### PHASE 13: Time Agent (Proactive Schedule Monitoring)

* **Purpose:** Build an automated agent that monitors time progression, detects silent evidence gaps on critical path tasks, and issues early warning delay alerts.
* **Inputs:** Integrated backend and schedule projector.
* **Expected Outputs:** Background monitoring service in `ai/` or `backend/`.
* **Dependencies:** PHASE 12.
* **Exit Criteria:** Time Agent correctly flags inactive critical path activities during simulated timeline progression.

---

### PHASE 14: Analytics + Institutional Memory Store

* **Purpose:** Implement long-term storage and analytical querying over human planner corrections, real-world task execution rates, and contractor productivity metrics.
* **Inputs:** Historical HITL corrections and verified actual durations.
* **Expected Outputs:** Institutional Memory service and analytical reporting module.
* **Dependencies:** PHASE 13.
* **Exit Criteria:** System captures planner overrides and displays comparative actual vs. baseline productivity benchmarks.

---

### PHASE 15: Testing + Benchmark Evaluation

* **Purpose:** Perform comprehensive end-to-end testing, matching precision/recall benchmarking, confidence score calibration, and system stress testing.
* **Inputs:** Full application stack and benchmark datasets.
* **Expected Outputs:** Test suite in `tests/` and benchmark evaluation report in `docs/10-testing/`.
* **Dependencies:** PHASE 14.
* **Exit Criteria:** Test suite passes with $\ge 90\%$ precision on synthetic ground truth benchmarks; zero critical regressions.

---

### PHASE 16: SIH Demo + Presentation Packaging

* **Purpose:** Prepare final SIH 2026 hackathon deliverables: live demo scripts, slide deck, presentation narrative, video walkthrough, and submission repository polish.
* **Inputs:** Operational SATYA system and evaluation metrics.
* **Expected Outputs:** Presentation materials in `docs/11-sih/` and verified demo pipeline.
* **Dependencies:** PHASE 15.
* **Exit Criteria:** End-to-end live demo runs flawlessly in under 5 minutes, demonstrating field observation ingestion to trusted schedule actuals.
