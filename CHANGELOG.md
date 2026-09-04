# Changelog

All notable changes to the SATYA project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).
## [0.17.0] - 2026-09-04

### Added (Phase 15 — Empirical System Validation)
- Completed and APPROVED & CLOSED `PHASE 15 — Empirical System Validation`.
- Added **Component 1: Workload Performance Benchmark** (`tests/integration/test_workload_performance.py`):
  - Small (50 events), Medium (500 events), Large (5,000 events across 5 projects) tiers.
  - p50/p95 latency measurements; empirical RSS memory tracking. No arbitrary SLA thresholds.
  - Measured: p50 ~3.2 ms/event, p95 ~3.9 ms/event (SQLite in-memory, single-threaded).
- Added **Component 2: Failure Recovery Tests** (same file):
  - Empty payload ValueError does not create orphaned source_document records.
  - Valid ingestion succeeds cleanly after a preceding failed ingestion.
- Added **Component 3: Controlled Safety Mutation Harness** (same file):
  - Mutation 1 — Rule 5 vocabulary guard: out-of-vocabulary raw Activity ID is cleared (never promoted).
  - Mutation 2 — Stale HITL snapshot lock: second v1 decision rejected with HTTP 409 STALE_REVIEW_STATE.
  - Mutation 3 — Match result immutability: CHANGE_MATCH does not retroactively alter original MatchResult row.
- Added **Component 4: DB Invariant Concurrency Stress Tests** (`tests/integration/test_concurrency_invariants.py`):
  - N=2, N=5, N=10 concurrent HITL review threads; exactly 1 wins, rest receive HTTP 409.
  - DB state invariant verified after each race: exactly 1 v2 TrustAssessment per event.
- Added **Component 5: Property Invariants Suite** (`tests/unit/test_property_invariants.py`):
  - 7 properties: provenance immutability, ID safety, trust monotonicity, idempotency,
    five-entity historical immutability, multi-tenant isolation, determinism across pipeline runs.
- Added **Component 6: Adversarial Robustness Suite** (`tests/unit/test_adversarial_suite.py`):
  - Structural corruption (malformed/empty payloads), linguistic adversarial inputs,
    semantic noise, and injection attack probes.
- Added **Component 7: Full Truth-Chain Benchmark & Confidence Calibration** (`tests/integration/test_truth_chain_benchmark.py`):
  - Ground-truth evaluation over 62 dev-set records across all 5 execution-intelligence layers.
  - Layer 1 Extraction Recall: 62/62 = 1.000; Layer 2 Matching Precision: 1.000, F1: 0.660;
    Layer 3 Trust Coverage: 63/63 = 1.000; Layer 4 Projection: 60 activities; Layer 5 Time Agent: 19 signals.
  - Confidence threshold sweep theta in {0.40..0.95}: precision = 1.000 at theta>=0.50.
  - ECE (10-bin): 0.1783 (empirically recorded, no hard pass/fail).
  - Post-benchmark historical immutability regression: v1 TrustAssessments intact, append-only ledger verified.
- Updated test suite to **134 total automated tests, 134 passing (0 failures)**.
- Updated `docs/00-governance/development-phases.md` to mark Phase 15 CLOSED.

---

## [0.16.0] - 2026-09-04

### Added (Phase 14 Analytics & Institutional Memory Store)
- Completed and 🟢 **APPROVED & CLOSED** `PHASE 14 — Analytics & Institutional Memory Store`.
- Implemented domain models in `backend/models/domain_models.py`: `AliasStatus`, `BenchmarkStatus`, `InstitutionalMemoryPolicy`, `MemoryDistillationRun`, `TerminologyAliasRecord`, `ExecutionRateBenchmark`, `ContractorReportingProfile`, `ConflictResolutionPattern`.
- Implemented `InstitutionalMemoryService` (`backend/analytics/memory_service.py`):
  - Auditable memory distillation run tracking.
  - Terminology alias promotion lifecycle (`CANDIDATE` $\rightarrow$ `VALIDATED` $\rightarrow$ `ACTIVE` $\rightarrow$ `SUPERSEDED`).
  - Multi-factor alias confidence math: $C_{\text{alias}} = \text{clamp}(w_{\text{plan}} N_{\text{planners}} + w_{\text{src}} N_{\text{sources}} + R(\Delta t) - w_{\text{over}} N_{\text{reoverrides}}, 0.0, 1.0)$.
  - Configurable `InstitutionalMemoryPolicy` weights ($w_{\text{plan}} = 0.3$, $w_{\text{src}} = 0.2$, $w_{\text{over}} = 0.4$, $T_{1/2} = 90$ days).
  - Strictly project-scoped alias lookup (`project_id`).
- Implemented `ExecutionAnalyticsEngine` (`backend/analytics/analytics_engine.py`):
  - UOM and quantity-basis compatible rate benchmarking.
  - Sample-size threshold gating (`INSUFFICIENT_SAMPLE` for $N < 3$, `PROVISIONAL` for $3 \le N < 10$, `VALIDATED` for $N \ge 10$).
  - Explicit planned rate formula with `None` handling for missing baseline values.
  - Contractor Reporting & Verification Profile with reporting latency ($t_{\text{reported}} - t_{\text{observed}}$) and nullable contractor ID.
  - Conflict & Warning resolution pattern tracking with separation of Time Agent acknowledgments vs physical condition resolutions.
- Integrated additive alias factor ($S_{\text{alias}}$) into `ScheduleAwareMatchingEngine` (`backend/matching/matching_engine.py`) and `ScheduleMatchingService` (`backend/services/matching_service.py`).
- Added REST API routes for memory and analytics (`backend/api/routes_analytics.py`, `backend/api/app.py`).
- Added ES6 dynamic Analytics & Memory tab view component to Phase 12 Frontend Console (`frontend/js/views/analytics_memory.js`, `frontend/js/api_client.js`, `frontend/js/app.js`, `frontend/index.html`).
- Created unit and integration test suite (`tests/unit/test_institutional_memory.py`, `tests/unit/test_execution_analytics.py`, `tests/integration/test_analytics_integration.py`). Extended test coverage to **99 total automated tests** passing 100%.
- Verified matching evaluation benchmark before and after memory activation using `scripts/evaluate_matching_engine.py`.
- Published core engine specification `docs/05-core-engines/institutional-memory-analytics.md`.

---

## [0.15.0] - 2026-09-04

### Added (Phase 13 Time Agent - Proactive Schedule Monitoring Engine)
- Completed and 🟢 **APPROVED & CLOSED** `PHASE 13 — Time Agent (Proactive Schedule Monitoring Engine)`.
- Extended domain models in `backend/models/domain_models.py` with `TemporalSignalType`, `SignalSeverity`, `SignalStatus`, `TemporalMonitoringPolicy`, `MonitoringEvaluationRun`, and `TemporalWarningSignal`.
- Implemented deterministic policy-driven monitoring engine in `backend/monitoring/time_agent_engine.py`:
  - 6 early-warning evaluation rules: `SILENT_CRITICAL_PATH_RISK`, `OUT_OF_SEQUENCE_EXECUTION`, `FORECAST_FINISH_SLIPPAGE`, `EVIDENCE_COVERAGE_GAP`, `STAGNANT_IN_PROGRESS`, `UNTRUSTED_CLAIM_ACCUMULATION`.
  - Null-forecast safe slippage calculation and explicit rationale traces for every warning signal.
  - Strict `as_of_date` temporal bounding ($t_{\text{observed}} \le t_{\text{as\_of}}$).
- Implemented service orchestration & SQLite persistence in `backend/monitoring/time_agent_service.py` and `backend/persistence/database_engine.py`:
  - Persistent tables `monitoring_evaluation_runs` and `temporal_warning_signals`.
  - Auditable evaluation run tracking and signal deduplication via `signal_key` (`{project_id}|{activity_id}|{signal_type}`).
  - Automatic signal lifecycle management (`ACTIVE`, `RESOLVED`, `SUPERSEDED`, `ACKNOWLEDGED`).
- Exposed REST API monitoring endpoints (`backend/api/routes_monitoring.py` and `backend/api/app.py`):
  - `POST /api/v1/monitoring/evaluate`
  - `GET /api/v1/monitoring/projects/{id}/signals`
  - `GET /api/v1/monitoring/signals/{id}`
  - `POST /api/v1/monitoring/signals/{id}/acknowledge`
- Integrated Time Agent Monitoring into Phase 12 Frontend Console (`frontend/js/api_client.js`, `frontend/js/formatters.js`, `frontend/js/views/control_tower.js`).
- Extended test coverage to **88 total automated tests** (74 unit tests, 14 integration tests) passing 100%.
- Published canonical specification `docs/05-core-engines/time-agent-monitoring.md`.

---

## [0.14.0] - 2026-09-04

### Added (Phase 12 Frontend Planner Dashboard & HITL Interface)
- Completed and 🟢 **APPROVED & CLOSED** `PHASE 12 — Frontend Planner Dashboard & HITL Interface`.
- Implemented zero-dependency, zero-CDN ES6 module web application in `frontend/`:
  - Design system tokens, layout grid, and high-density dark slate engineering console styles (`frontend/css/`).
  - REST API Client (`frontend/js/api_client.js`) communicating with `http://127.0.0.1:8000/api/v1`.
  - Application state manager (`frontend/js/state.js`) with dynamic project discovery (`PRJ-NBG-2026`, `PRJ-SCP-2026`).
  - Formatting helpers & "Why SATYA Believes This" factor renderer (`frontend/js/formatters.js`).
  - Control Tower Dashboard View (`frontend/js/views/control_tower.js`).
  - Reconciliation Desk View (`frontend/js/views/reconciliation_desk.js`) with 6-step visual hierarchy & snapshot locked decision form.
  - Evidence & Provenance Center View (`frontend/js/views/evidence_center.js`).
  - Schedule Explorer View (`frontend/js/views/schedule_explorer.js`) with SATYA Overlay.
  - App router and operational health monitor (`frontend/js/app.js`, `frontend/index.html`).
- Added read-model provenance trace endpoint `GET /api/v1/evidence/events/{event_id}/trace` to Phase 11 (`backend/api/routes_evidence.py`).
- Updated executable server runner `scripts/run_server.py` to serve `frontend/` static assets under `/` while routing `/api/v1/*` REST requests.
- Extended test suite to 82 total tests (69 unit tests, 13 integration tests) passing 100%.
- Published canonical frontend documentation `docs/09-frontend/frontend-app.md`.

---

## [0.13.0] - 2026-09-04

### Added (Phase 11 Backend Application Services & REST API)
- Completed and 🟢 **APPROVED & CLOSED** `PHASE 11 — Backend Application Services`.
- Implemented thin HTTP application layer in `backend/api/`:
  - `SATYAError` exception and standardized error response formatter (`backend/api/errors.py`).
  - Transport serializers for all domain models (`backend/api/serializers.py`).
  - Automatic OpenAPI 3.0 specification generator (`backend/api/openapi.py`).
  - Ingestion route handler (`backend/api/routes_ingestion.py`).
  - Fingerprints route handler (`backend/api/routes_fingerprints.py`).
  - Matching route handler (`backend/api/routes_matching.py`).
  - Evidence & Trust route handler (`backend/api/routes_evidence.py`).
  - HITL Review Queue & Decision route handler (`backend/api/routes_hitl.py`) with REST Snapshot Lock `HTTP 409 Conflict` enforcement.
  - Schedule Projection route handler (`backend/api/routes_projections.py`).
  - Main `SATYAApplicationAPI` HTTP router & CORS middleware (`backend/api/app.py`).
- Implemented CLI server runner script `scripts/run_server.py`.
- Added API unit and integration test suites (`tests/unit/test_api_endpoints.py`, `tests/unit/test_api_hitl_concurrency.py`, `tests/integration/test_api_integration.py`).
- Extended test coverage to 81 total tests (68 unit tests, 13 integration tests) passing 100%.
- Published canonical REST API documentation `docs/08-api/backend-api.md`.

---

## [0.12.0] - 2026-09-04

### Added (Phase 10 Actual Progress + Schedule Projection Engine)
- Completed and 🟢 **APPROVED & CLOSED** `PHASE 10 — Actual Progress + Schedule Projection Engine`.
- Implemented domain models in `backend/models/domain_models.py`: `ActivityProgress`, `WBSProgress`, `ScheduleProjection`, `ProgressCalculationPolicy`, `QuantityObservationType`, `ProgressCalculationStatus`, `ForecastStatus`, `ProgressWeightPolicy`, `ActivityProgressStatus`, `QAClearanceStatus`.
- Implemented `ActualProgressEngine` (`backend/projection/actual_progress_engine.py`) establishing a baseline-immutable, recomputable derived `ProgressLayer` over the Execution Truth Ledger.
- Implemented Policy-Based Progress Calculation (`QUANTITY_BASED`, `MILESTONE_BASED`, `STATUS_BASED`).
- Implemented Quantity Observation Type Resolution (`CUMULATIVE_TOTAL` vs `DAILY_DELTA` vs `UNKNOWN`).
- Implemented Event Contribution Filtering for Actual Start (derived strictly from `START`, `PROGRESS`, `QUANTITY_UPDATE`, `RESUME` events).
- Implemented Defensible Forecast Engine with Null-Forecast Safety (`ForecastStatus` returns `INSUFFICIENT_HISTORY` / `ZERO_RATE` and `forecast_finish = None` when evidence/history is insufficient).
- Implemented QA Clearance separation (`qa_clearance_status`), allowing 100% physical completion while QA clearance remains `PENDING`.
- Implemented Duration-Weighted WBS Rollup (`ProgressWeightPolicy`) with mixed-unit safety (`physical_progress_pct = None`).
- Implemented Baseline Authority Schedule Variances ($SV_{\text{finish}}$) and Critical Activity Projected Delay (`critical_activity_projected_delay`).
- Implemented Retained Unverified Progress Claims tracking (`unverified_event_count`, `unverified_reported_quantity`).
- Implemented `ScheduleProjectionService` (`backend/projection/projection_service.py`) orchestrating project snapshot generation and SQLite persistence.
- Extended `DatabaseEngine` (`backend/persistence/database_engine.py`) with `schedule_projections` table.
- Published core engine specification `docs/05-core-engines/schedule-projection.md`.
- Expanded test suite to 61 unit and integration tests passing 100%.

---

## [0.11.0] - 2026-09-04

### Added (Phase 9 Human Validation HITL Workflow)
- Completed and 🟢 **APPROVED & CLOSED** `PHASE 9 — Human Validation (HITL) Workflow`.
- Implemented core domain models in `backend/models/domain_models.py`: `ValidationDecisionType` (`VALIDATE`, `CHANGE_MATCH`, `REJECT`, `REQUEST_EVIDENCE`, `DEFER`), `OverrideReasonCategory`, `QueuePriority`, `ValidationDecision`, `PlannerCorrectionRecord`, and `PlannerQueueItem`.
- Implemented `PlannerQueueManager` (`backend/hitl/queue_manager.py`) prioritizing review queue items by severity ($P1$ Critical > $P2$ High/Ambiguous > $P3$ Medium/Gap > $P4$ Low Confidence) with deterministic tie-breaking.
- Implemented `ValidationService` (`backend/hitl/validation_service.py`) providing 5 explicit decision handlers (`validate_event`, `change_match`, `reject_event`, `request_evidence`, `defer_event`).
- Enforced non-mutating audit trails: planner re-mapping (`CHANGE_MATCH`) creates a new `ValidationDecision` record, a versioned `TrustAssessment v(N+1)`, and a derived `PlannerCorrectionRecord` without mutating existing `MatchResult` or `ExecutionEvent` records (`UPDATE` SQL statements strictly prohibited).
- Enforced Decision State Snapshot Lock (`reviewed_trust_version`, `reviewed_match_result_id`, `reviewed_evidence_assessment_id`) preventing race conditions during review.
- Enforced Rule 5 schedule vocabulary guardrails on planner re-mapping (`new_activity_id` must exist in baseline schedule).
- Extended `DatabaseEngine` (`backend/persistence/database_engine.py`) with append-only tables `validation_decisions` and `planner_corrections`.
- Published core engine specification `docs/05-core-engines/human-validation-hitl.md`.
- Expanded test suite to 44 unit and integration tests passing 100%.

---

## [0.10.0] - 2026-09-04

### Added (Phase 8 Evidence, Confidence & Conflict Engine)
- Completed `PHASE 8 — Evidence + Confidence + Conflict Engine`.
- Implemented `EvidenceClaim` domain model in `backend/models/domain_models.py` decomposing source fragments into atomic claims (status, quantity, progress, QA, location, temporal).
- Implemented `ClaimExtractor` (`backend/evidence/claim_extractor.py`) extracting structured claims from execution events and fragments.
- Implemented `ReliabilityEvaluator` (`backend/evidence/reliability_evaluator.py`) assessing multi-factor evidence quality (authority, verification status, provenance completeness, timestamp quality, consistency).
- Implemented `CorroborationEngine` (`backend/evidence/corroboration_engine.py`) tracking `origin_group_id` to enforce true independent corroboration credit.
- Implemented `GapEngine` (`backend/evidence/gap_engine.py`) enforcing activity and discipline-aware `EvidenceRequirementPolicy` (e.g. mandatory QA clearance for piping/welding completion claims vs excavation).
- Implemented `ConflictEngine` (`backend/evidence/conflict_engine.py`) detecting 7 conflict categories (`TEMPORAL_CONFLICT`, `STATUS_CONFLICT`, `QUANTITY_CONFLICT`, `QA_CONFLICT`, `SCHEDULE_CONFLICT`, `LOCATION_CONFLICT`, `DUPLICATE_CONFLICT`) with reporting delay awareness, out-of-sequence semantics, and `DUPLICATE_EVIDENCE` separation.
- Implemented `TrustEvaluatorService` (`backend/services/trust_evaluator_service.py`) applying a deterministic gating tree (Match Sufficient? $\rightarrow$ Evidence Sufficient? $\rightarrow$ Severe Conflict Present? $\rightarrow$ Mandatory Gap Present?) to evaluate `TrustStatus` (`TRUSTED`, `REVIEW_REQUIRED`, `UNTRUSTED`).
- Extended `DatabaseEngine` (`backend/persistence/database_engine.py`) with append-only versioned tables: `evidence_ledger`, `evidence_claims`, `evidence_assessments`, `conflict_flags`, and `trust_assessments`.
- Published core engine specification `docs/05-core-engines/evidence-confidence-conflict.md`.
- Expanded test suite to 35 unit and integration tests passing 100%.

---

## [0.9.1] - 2026-09-04

### Changed / Hardened (Phase 7.1 Calibration & Failure Analysis Pass)
- Completed and 🟢 **APPROVED** `PHASE 7.1 — Matching Engine Calibration & Failure Analysis`.
- Upgraded `MatchOutcome` enum in `backend/models/domain_models.py` to add `INSUFFICIENT_EVIDENCE` (distinct from `AMBIGUOUS` and `UNMATCHED`).
- Added `missing_discriminators` field to `MatchResult` dataclass to identify explicit missing locators (`line_number`, `chainage_km_range`, `equipment_tag`) for planner action.
- Upgraded `ScheduleAwareMatchingEngine` (`backend/matching/matching_engine.py`) with Stage 1 Hard Constraints Filter (project identity, discipline contradiction, chainage non-overlap) and Stage 2 Discriminative Multi-Factor Ranking.
- Implemented `parse_chainage_range` parsing interval bounds ($Km\ X.X\ \text{to}\ Y.Y$ and $CH\ X+XXX$) for spatial overlap matching.
- Eliminated "Missing explicit Activity ID = Ambiguous" fallacy; unambiguous multi-factor spatial, discipline, and terminology evidence now produces high-confidence `MATCHED` outcomes without explicit Activity IDs.
- Fixed cached event dictionary conversion in `ExecutionEventPipelineService` (`backend/services/pipeline_service.py`) for duplicate source document payloads.
- Expanded discipline keywords in `backend/extraction/event_extractor.py` to recognize field report shorthands (`civ`, `pip`, `str`, `mec`, `ele`, `ins`, `qa_`, `radiogr`).
- Upgraded `scripts/evaluate_matching_engine.py` into a full benchmark evaluation harness measuring candidate retrieval (`Recall@1`, `Recall@3`, `Recall@5`, `Recall@10`), outcome precision, and failure taxonomy breakdown (`RETRIEVAL_FAILURE`, `RANKING_FAILURE`, `GENUINE_AMBIGUITY`, `INSUFFICIENT_EVIDENCE`, `EXTRACTION_FAILURE`).
- Updated specification document `docs/05-core-engines/schedule-matching.md`.
- Expanded unit and integration test suite to 27 tests passing 100%.

---

## [0.9.0] - 2026-09-04

### Added
- Completed `PHASE 7 — Schedule-Aware Activity Matching Engine`.
- Implemented matching engine domain models in `backend/models/domain_models.py`: `MatchOutcome`, `MatchFactorScores`, `CandidateMatch`, `MatchResult`.
- Implemented `ScheduleAwareMatchingEngine` (`backend/matching/matching_engine.py`) with multi-factor weighted scoring (explicit ID, line/equipment, spatial/chainage, WBS, discipline, terminology action, temporal window) and configurable outcome classification (`MATCHED`, `AMBIGUOUS`, `UNMATCHED`).
- Extended `DatabaseEngine` (`backend/persistence/database_engine.py`) with `match_results` SQLite repository table.
- Implemented `ScheduleMatchingService` (`backend/services/matching_service.py`) orchestrating event-to-fingerprint matching.
- Created `scripts/evaluate_matching_engine.py` benchmarking matching engine against synthetic ground truth datasets (`ground_truth_dev.json`, `ground_truth_edge_cases.json`, `ground_truth_eval.json`).
- Published `docs/05-core-engines/schedule-matching.md` specification document.
- Expanded test suite to 25 unit and integration tests passing 100%.

---

## [0.8.0] - 2026-09-04

### Added
- Completed `PHASE 6 — Activity Fingerprinting Engine`.
- Implemented `ActivityFingerprint` domain dataclass in `backend/models/domain_models.py` capturing structural, semantic, spatial, temporal, and terminology intelligence layers.
- Implemented `TerminologyIntelligenceEngine` (`backend/fingerprinting/terminology_engine.py`) providing Oil & Gas EPC abbreviation expansion (`ROW`, `HDD`, `GGS`, `NDT`, `DCS`, `TPIA`), action verb extraction, and field alias generation.
- Implemented `ActivityFingerprintGenerator` (`backend/fingerprinting/fingerprint_generator.py`) for WBS hierarchy topological path resolution and multi-dimensional fingerprint computation.
- Extended `DatabaseEngine` (`backend/persistence/database_engine.py`) with `activity_fingerprints` SQLite repository table.
- Implemented `ActivityFingerprintService` (`backend/services/fingerprint_service.py`) indexing 100% of baseline activities across synthetic project schedules (`PRJ-NBG-2026` & `PRJ-SCP-2026`, 101 activities total).
- Published `docs/05-core-engines/activity-fingerprinting.md` specification.
- Implemented unit and integration test suite (`tests/unit/test_fingerprinting.py`, `tests/integration/test_fingerprint_integration.py`) passing 100%.

---

## [0.7.1] - 2026-09-04

### Changed / Hardened (Phase 5.1 Correction Pass)
- Implemented **One-to-Many Event Decomposition** (`extract_events_from_fragment`) splitting compound field fragments into multiple discrete `ExecutionEvent` records.
- Implemented **Raw Activity ID Preservation**: invalid explicit references (e.g. `PIP-9999`) are preserved in `raw_observed_activity_id` and tagged `INVALID_EXPLICIT_REFERENCE` while `observed_activity_id` is set to `None`, preserving 100% of field observation data.
- Implemented **Field-Level Provenance Spans**: `ProvenanceRecord.field_provenance_map` records character start/end spans (`start_char`, `end_char`, `snippet`) for extracted entities.
- Implemented **Temporal Uncertainty & Resolution Status**: relative dates ("yesterday") without valid reference submission dates return `observed_timestamp = None` and `UNRESOLVED_RELATIVE_DATE`.
- Verified **Strict Append-Only Immutability**: zero `UPDATE execution_events` SQL statements exist.
- Implemented zero-dependency `XLSXAdapter` (`backend/ingestion/xlsx_adapter.py`) using Python standard library `zipfile` and `xml.etree.ElementTree`.
- Expanded test suite to 23 unit & integration tests with 100% pass rate.

---

## [0.7.0] - 2026-09-04

### Added
- Completed `PHASE 5 — Execution Event Pipeline` vertical slice.
- Implemented modular Python backend architecture: `ingestion`, `normalization`, `extraction`, `validation`, `persistence`, and `services`.
- Implemented `SourceIngestionService` with SHA-256 hashing and exact duplicate detection idempotency.
- Implemented `ContentNormalizationService` for whitespace cleanup, segment fragmenting, and relative date resolution.
- Implemented `ExecutionEventExtractionService` with hybrid regex entity extraction for actions, disciplines, quantities, units, locations, and Phase 4.5 real-world fields (`shift_context`, `pending_qa_clearance`, `remaining_quantity`, `work_front_tag`).
- Implemented `ClosedVocabularyGuardrail` (Rule 5) to prevent hallucinated Activity IDs; invalid IDs reset to `None` and quarantined.
- Implemented `DatabaseEngine` (SQLite) append-only persistence for documents, fragments, events, provenance, and quarantine records.
- Implemented `ExecutionEventPipelineService` orchestrator with correlation ID structured logging.
- Created architectural and AI documentation: `docs/04-architecture/technology-stack.md`, `docs/05-core-engines/execution-event-pipeline.md`, `docs/07-ai/extraction-pipeline.md`, `docs/07-ai/guardrails.md`, `docs/07-ai/evaluation.md`.
- Implemented 18 unit & integration tests (`tests/unit/`, `tests/integration/`) with 100% pass rate.

---

## [0.6.0] - 2026-09-04

### Added
- Completed `PHASE 4.5 — Real-World Data Reconnaissance`.
- Formulated real-world data source register in `docs/06-data/real-world-source-register.md` classifying investigated public infrastructure sources across 4 standard categories (`[BENCHMARK_CANDIDATE]`, `[REFERENCE_MATERIAL]`, `[MANUALLY_LABELABLE]`, `[UNSUITABLE]`).
- Conducted real-world human execution language pattern analysis (heavy abbreviations, mixed/dual units, shift context, QA hold points, partial completion, compound sentences).
- Conducted synthetic dataset gap analysis and proposed conceptual domain extensions (`shift_context`, `pending_qa_clearance`, `remaining_quantity`, `work_front_tag`).
- Published 3-tier real-world benchmark strategy in `docs/06-data/real-world-data-strategy.md` enforcing strict non-training data principles and licensing safeguards.

---

## [0.5.1] - 2026-09-04

### Changed / Added (Phase 4 Correction Pass)
- Executed strict Phase 4 Integrity Review and expanded synthetic dataset to genuinely satisfy all original exit criteria.
- Created second complete project baseline: *"Subansiri Crude Oil Pipeline Replacement & Offsite Infrastructure"* (`PRJ-SCP-2026`) containing 41 L5/L6 activities. Total activities across both projects expanded to 101.
- Audit and expanded discipline coverage to 8 complete engineering disciplines.
- Expanded field observation corpus to 107 multi-format records.
- Created dataset validation script in `scripts/validate_synthetic_data.py` (100% integrity validation PASS).

---

## [0.5.0] - 2026-09-04

### Added
- Completed `PHASE 4 — Synthetic Data Engineering`.

---

## [0.4.0] - 2026-09-04

### Added
- Completed `PHASE 3 - Architecture + Data Model`.

---

## [0.3.0] - 2026-09-04

### Added
- Completed `PHASE 2 - Product + Requirements`.

---

## [0.2.0] - 2026-09-04

### Added
- Completed `PHASE 1 - Problem + Domain Understanding`.

---

## [0.1.0] - 2026-09-04

### Added
- Established `PHASE 0 - Foundation` repository governance.
