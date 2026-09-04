> **Current Status:** `PHASE 15 — Empirical System Validation` (🟢 APPROVED & CLOSED)  

---

## Lifecycle Overview

The SATYA project strictly adheres to a sequential 17-phase implementation lifecycle. No implementation work (coding, package installation, database setup) may proceed outside the currently active phase.

---

## Phase Status Summary

* **Phase 0–5.1:** 🟢 APPROVED
* **Phase 6:** 🟢 APPROVED
* **Phase 7:** 🟡 BASELINE / KNOWN LIMITATIONS (75% Recall@10, 12.5% Recall@1, 0% automatic match coverage at default threshold)
* **Phase 7.1:** 🟢 APPROVED (Calibration & Failure Audit completed)
* **Phase 8:** 🟢 APPROVED (Evidence + Confidence + Conflict Engine completed)
* **Phase 9:** 🟢 APPROVED & CLOSED (Human Validation / HITL Workflow completed)
* **Phase 10:** 🟢 APPROVED & CLOSED (Actual Progress + Schedule Projection Engine completed)
* **Phase 11:** 🟢 APPROVED & CLOSED (Backend Application Services & REST API completed)
* **Phase 12:** 🟢 APPROVED & CLOSED (Frontend Planner Dashboard & HITL Interface completed)
* **Phase 13:** 🟢 APPROVED & CLOSED (Time Agent Proactive Schedule Monitoring Engine completed)
* **Phase 14:** 🟢 APPROVED & CLOSED (Analytics + Institutional Memory Store completed)
* **Phase 15:** 🟢 APPROVED & CLOSED (Empirical System Validation completed)
* **Phase 16:** ▶ ACTIVE / NEXT (SIH Demo + Presentation Packaging)

---

## Phase Definitions

### PHASE 10: Actual Progress + Schedule Projection Engine

* **Purpose:** Implement `ActualProgressEngine` (`backend/projection/actual_progress_engine.py`) and `ScheduleProjectionService` (`backend/projection/projection_service.py`) deriving activity progress, forecast finish dates, calculation statuses, and schedule variances from trusted execution events while maintaining strict read-only baseline immutability.
* **Inputs:** Baseline schedule JSON files (`baseline_schedule.json`), `ExecutionEvents` (Phase 5), `TrustAssessments` (Phase 8), `ValidationDecisions` (Phase 9).
* **Expected Outputs:** Core calculation engine, `ScheduleProjection` domain models, `schedule_projections` SQLite repository table, engine specification (`docs/05-core-engines/schedule-projection.md`), and passing unit/integration tests (`tests/unit/test_schedule_projection.py`, `tests/integration/test_projection_integration.py`).
* **Governance Status:** 🟢 **APPROVED & CLOSED**
* **Approved Governance Directive:**
  > **Phase 10 — APPROVED & CLOSED**  
  > Policy-based progress calculation (`QUANTITY_BASED`, `MILESTONE_BASED`, `STATUS_BASED`), cumulative vs delta quantity resolution (`CUMULATIVE_TOTAL` vs `DAILY_DELTA`), event contribution filtering for actual start, null-safe forecast engine (`ForecastStatus`), QA clearance separation (`qa_clearance_status`), duration-weighted WBS rollups (`ProgressWeightPolicy`), baseline-authority schedule variances ($SV_{\text{finish}}$), and unverified progress claims retention are fully operational. Baseline schedule files remain 100% read-only and immutable. All 61 unit and integration tests pass 100%.  
  >  
  > **Next Phase:** PHASE 11 — Backend Application Services.

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

* **Purpose:** Implement `EvidenceClaim` extraction, multi-factor evidence reliability assessment, origin-group aware corroboration, discipline-aware evidence requirement policies, explicit 7-category conflict detection, and deterministic gating tree trust evaluation.
* **Inputs:** `ExecutionEvent` (Phase 5), `ActivityFingerprint` (Phase 6), `MatchResult` (Phase 7).
* **Expected Outputs:** Core engines (`backend/evidence/`), `TrustEvaluatorService` (`backend/services/trust_evaluator_service.py`), append-only versioned SQLite ledger tables, and engine specification (`docs/05-core-engines/evidence-confidence-conflict.md`).
* **Governance Status:** 🟢 **APPROVED & CLOSED**
* **Approved Governance Directive:**
  > **Phase 8 — APPROVED & CLOSED**  
  > `EvidenceClaim` atomic decomposition, multi-factor reliability assessment ($S_{\text{auth}}, S_{\text{verif}}, S_{\text{prov}}, S_{\text{time}}, S_{\text{cons}}$), origin-group aware corroboration, activity/discipline-aware evidence requirement policies, explicit 7-category conflict detection (with reporting delay and out-of-sequence semantics), and deterministic gating tree trust evaluation are fully operational. Persists versioned `TrustAssessment` records ($v1 \rightarrow v2$) in append-only SQLite storage with 35/35 passing tests.  
  >  
  > **Product Language Constraint:** SATYA determines whether reported execution is sufficiently evidenced and internally consistent to be treated as trusted execution truth under configured policies. It does NOT claim to physically verify or prove execution reality without a validated verification mechanism.  
  >  
  > **Next Phase:** PHASE 9 — Human Validation (HITL) Workflow.

---

### PHASE 9: Human Validation (HITL) Workflow

* **Purpose:** Implement planner review queue management, decision workspace domain models, 5 explicit decision handlers (`VALIDATE`, `CHANGE_MATCH`, `REJECT`, `REQUEST_EVIDENCE`, `DEFER`), decision state snapshot locks, non-mutating audit trails, and Phase 14 institutional memory hooks.
* **Inputs:** Flagged matches (`AMBIGUOUS`, `UNMATCHED`, `INSUFFICIENT_EVIDENCE`) and trust assessments (`REVIEW_REQUIRED`, `UNTRUSTED`) from Phase 8.
* **Expected Outputs:** Queue manager (`backend/hitl/queue_manager.py`), Validation service (`backend/hitl/validation_service.py`), append-only tables `validation_decisions` & `planner_corrections`, core engine spec (`docs/05-core-engines/human-validation-hitl.md`), and passing unit/integration tests (`tests/unit/test_hitl_workflow.py`, `tests/integration/test_hitl_integration.py`).
* **Governance Status:** 🟢 **APPROVED & CLOSED**
* **Approved Governance Directive:**
  > **Phase 9 — APPROVED & CLOSED**  
  > Human Validation (HITL) Workflow is fully operational. Prioritizes review queue items by severity ($P1 > P2 > P3 > P4$), enforces Decision State Snapshot Lock preventing race conditions during review, validates `CHANGE_MATCH` targets against baseline schedule vocabulary (Rule 5), and generates versioned `TrustAssessment v(N+1)` and `PlannerCorrectionRecord` without mutating existing match or event histories. All 44 unit and integration tests pass 100%.  
  >  
  > **Next Phase:** PHASE 10 — Actual Progress + Schedule Projection Engine.

---

### PHASE 11: Backend Application Services

* **Purpose:** Package execution event pipelines, matching engines, scoring modules, trust evaluators, HITL review queues, and progress projectors into clean, documented REST application services.
* **Inputs:** Modules from Phase 5 through Phase 10.
* **Expected Outputs:** Runnable backend service codebase in `backend/api/`, `scripts/run_server.py`, REST API documentation in `docs/08-api/backend-api.md`, and passing unit/integration test suite (`tests/unit/test_api_endpoints.py`, `tests/unit/test_api_hitl_concurrency.py`, `tests/integration/test_api_integration.py`).
* **Governance Status:** 🟢 **APPROVED & CLOSED**
* **Approved Governance Directive:**
  > **Phase 11 — APPROVED & CLOSED**  
  > Thin transport REST API layer (`SATYAApplicationAPI`) operational over existing SATYA intelligence services with zero business logic inside route handlers. Includes thin domain serializers, standardized `SATYAError` response model, OpenAPI 3.0 schema generation (`/api/v1/openapi.json`), configurable CORS middleware, operational health endpoint (`/api/v1/health`), and REST decision state snapshot locking (`HTTP 409 Conflict` on `STALE_REVIEW_STATE`). All 81 unit and integration tests pass 100%.  
  >  
  > **Next Phase:** PHASE 12 — Frontend Planner Dashboard & HITL Interface.

---

### PHASE 12: Frontend Planner Dashboard & HITL Interface

* **Purpose:** Develop the user-facing web interface for project planners and managers (Control Tower Dashboard, Reconciliation Desk, Evidence Center, Schedule Explorer).
* **Inputs:** Backend REST APIs (Phase 11) and UX specs (`docs/09-frontend/frontend-app.md`).
* **Expected Outputs:** Zero-build, zero-CDN ES6 web application (`frontend/`), static server integration in `scripts/run_server.py`, frontend documentation (`docs/09-frontend/frontend-app.md`), and passing test suite (`82` total tests passing 100%).
* **Governance Status:** 🟢 **APPROVED & CLOSED**
* **Approved Governance Directive:**
  > **Phase 12 — APPROVED & CLOSED**  
  > Zero-dependency, presentation-only web application (`frontend/`) operational over Phase 11 REST APIs with zero domain-level calculations in JavaScript. Features Control Tower Dashboard, Reconciliation Desk (HITL centerpiece with 6-step visual hierarchy and snapshot-locked decision forms with `HTTP 409 Conflict` stale-state handling), Evidence & Provenance Center (full trace visualizer), and Schedule Explorer (SATYA Overlay). Built using native system font stacks and inline SVG icons for 100% offline SIH demo execution. All 82 unit and integration tests pass 100%.  
  >  
  > **Next Phase:** PHASE 13 — Time Agent (Proactive Schedule Monitoring).

---

### PHASE 13: Time Agent (Proactive Schedule Monitoring Engine)

* **Purpose:** Build a deterministic, policy-driven temporal monitoring engine (`backend/monitoring/time_agent_engine.py`, `time_agent_service.py`) that monitors schedule baselines, actual progress, evidence coverage gaps, and schedule projections to generate auditable early-warning temporal signals.
* **Inputs:** Baseline schedule JSON files, `ExecutionEvents`, `ScheduleProjection`, `TrustAssessments`, `ValidationDecisions`.
* **Expected Outputs:** `TimeAgentEngine`, `TimeAgentService`, `TemporalMonitoringPolicy`, `MonitoringEvaluationRun`, `TemporalWarningSignal`, persistent SQLite tables `monitoring_evaluation_runs` and `temporal_warning_signals`, REST API monitoring routes (`backend/api/routes_monitoring.py`), Control Tower UI early-warning feed, canonical specification (`docs/05-core-engines/time-agent-monitoring.md`), and passing unit/integration tests (`tests/unit/test_time_agent_engine.py`, `tests/integration/test_monitoring_integration.py`).
* **Governance Status:** 🟢 **APPROVED & CLOSED**
* **Approved Governance Directive:**
  > **Phase 13 — APPROVED & CLOSED**  
  > Deterministic policy-driven temporal monitoring engine implemented with strict `as_of_date` temporal bounding ($t_{\text{observed}} \le t_{\text{as\_of}}$), null-forecast safe slippage calculations, unique `signal_key` deduplication (`{project_id}|{activity_id}|{signal_type}`), explicit "Why SATYA Believes This" rationale traces, and auditable evaluation runs (`MonitoringEvaluationRun`). Enforces 6 warning signal evaluation rules: `SILENT_CRITICAL_PATH_RISK`, `OUT_OF_SEQUENCE_EXECUTION`, `FORECAST_FINISH_SLIPPAGE`, `EVIDENCE_COVERAGE_GAP`, `STAGNANT_IN_PROGRESS`, and `UNTRUSTED_CLAIM_ACCUMULATION`. Exposed via REST API (`/api/v1/monitoring/*`) and integrated into Phase 12 Control Tower Dashboard with manual signal acknowledgment. All 88 unit and integration tests pass 100%.  
  >  
  > **Next Phase:** PHASE 14 — Analytics + Institutional Memory Store.

---

### PHASE 14: Analytics & Institutional Memory Store

* **Purpose:** Build an auditable, versioned, project-aware institutional memory layer and empirical execution analytics engine (`backend/analytics/memory_service.py`, `analytics_engine.py`) that captures terminology alias mappings, computes UOM-safe productivity rate benchmarks, tracks contractor reporting verifiability, and analyzes conflict/warning resolution patterns.
* **Inputs:** Historical `ValidationDecision`, `PlannerCorrectionRecord`, `ExecutionEvent`, `ActivityProgress`, `ConflictFlag`, and `TemporalWarningSignal` records.
* **Expected Outputs:** `InstitutionalMemoryService`, `ExecutionAnalyticsEngine`, `InstitutionalMemoryPolicy`, `MemoryDistillationRun`, `TerminologyAliasRecord`, `ExecutionRateBenchmark`, `ContractorReportingProfile`, `ConflictResolutionPattern`, persistent SQLite tables `memory_distillation_runs`, `terminology_aliases`, `execution_rate_benchmarks`, `contractor_reporting_profiles`, `conflict_resolution_patterns`, REST API analytics routes (`backend/api/routes_analytics.py`), Analytics & Memory tab view component (`frontend/js/views/analytics_memory.js`), core engine specification (`docs/05-core-engines/institutional-memory-analytics.md`), and passing test suite (`99` total tests passing 100%).
* **Governance Status:** 🟢 **APPROVED & CLOSED**
* **Approved Governance Directive:**
  > **Phase 14 — APPROVED & CLOSED**  
  > Auditable institutional memory and empirical analytics engine implemented with strict non-rewriting historical immutability. Distills planner corrections into versioned terminology aliases with explicit lifecycle state transitions (`CANDIDATE` $\rightarrow$ `VALIDATED` $\rightarrow$ `ACTIVE` $\rightarrow$ `SUPERSEDED`), deterministic confidence scoring ($C_{\text{alias}} = \text{clamp}(w_{\text{plan}} N_{\text{planners}} + w_{\text{src}} N_{\text{sources}} + R(\Delta t) - w_{\text{over}} N_{\text{reoverrides}}, 0.0, 1.0)$), configurable weights via `InstitutionalMemoryPolicy`, and strict project scoping (`project_id`). Active aliases supply an additive factor boost ($S_{\text{alias}}$) to future candidate scoring without overriding schedule vocabulary safety or threshold bounds ($\theta_{\text{match}}$). Computes UOM-safe productivity rate benchmarks with sample size thresholding (`INSUFFICIENT_SAMPLE` for $N < 3$, `PROVISIONAL` for $3 \le N < 10$, `VALIDATED` for $N \ge 10$), contractor reporting & verification profiles with observed-to-reported latency ($t_{\text{reported}} - t_{\text{observed}}$), and conflict/warning resolution pattern analytics separating Time Agent acknowledgments from physical resolutions. All 99 unit and integration tests pass 100%.  
  >  
  > **Next Phase:** PHASE 15 — Testing + Benchmark Evaluation.

---



---



### PHASE 15: Testing + Benchmark Evaluation

* **Purpose:** Perform comprehensive empirical system validation: workload benchmarking, concurrency invariant testing, adversarial robustness testing, property-based invariant verification, full truth-chain evaluation, and confidence calibration sweep.
* **Inputs:** Full SATYA stack (Phases 0-14) and ground-truth annotated datasets (`data/synthetic/ground-truth/`).
* **Expected Outputs:** 7 new test modules covering workload performance, failure recovery, controlled safety mutation, concurrency DB invariants, property invariants, adversarial robustness, and truth-chain benchmark.
* **Dependencies:** PHASE 14.
* **Governance Status:** 🟢 **APPROVED & CLOSED**
* **Approved Governance Directive:**
  > **Phase 15 — APPROVED & CLOSED**  
  > Empirical system validation executed across 7 categories. Full truth-chain benchmark (62 dev-set records): Layer 1 Extraction Recall 1.000, Layer 2 Matching Precision 1.000 / F1 0.660, Layer 3 Trust Coverage 1.000, Layer 4 Projection 60 activities, Layer 5 Time Agent 19 signals. Confidence threshold sweep (theta 0.40..0.95): precision = 1.000 at theta>=0.50; ECE = 0.1783 (empirically recorded). Workload benchmarks: p50 ~3.2 ms/event, p95 ~3.9 ms/event (SQLite in-memory). Concurrency N=2/5/10: exactly 1 winner per race, DB state invariants hold. Rule 5 vocabulary guard verified via controlled mutation (ACT-9999-HALLUCINATED cleared, not promoted). STALE_REVIEW_STATE and MatchResult immutability guards confirmed. 134 total automated tests, 134 passing, 0 failures.  
  >  
  > **Next Phase:** PHASE 16 — SIH Demo + Presentation Packaging.

---

### PHASE 16: SIH Demo + Presentation Packaging

* **Purpose:** Prepare final SIH 2026 hackathon deliverables: live demo scripts, slide deck, presentation narrative, video walkthrough, and submission repository polish.
* **Inputs:** Operational SATYA system and evaluation metrics.
* **Expected Outputs:** Presentation materials in `docs/11-sih/` and verified demo pipeline.
* **Dependencies:** PHASE 15.
* **Exit Criteria:** End-to-end live demo runs flawlessly in under 5 minutes, demonstrating field observation ingestion to trusted schedule actuals.
