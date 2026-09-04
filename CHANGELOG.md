# Changelog

All notable changes to the SATYA project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
