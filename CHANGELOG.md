# Changelog

All notable changes to the SATYA project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [0.5.0] - 2026-09-04

### Added
- Completed `PHASE 4 — Synthetic Data Engineering`.
- Established coherent fictional project: *"North Basin Gas Gathering & Processing Expansion"* (`PRJ-NBG-2026`).
- Created baseline schedule datasets (`baseline_schedule.json`, `baseline_schedule.csv`) containing 61 L5/L6 activities across 7 engineering disciplines.
- Formulated 15 domain challenge scenarios (`SCN-001` through `SCN-015`) covering exact matching, missing Activity IDs, site jargon, abbreviations, ambiguous candidates, unmatched scope, contradictory reports, duplicate transmittals, delayed reporting, relative dates, granularity mismatches, evidence gaps, out-of-sequence logic, and multi-source corroboration.
- Created heterogeneous synthetic source observations (`dpr_reports.json`) representing Excel DPRs, PDF reports, site diaries, supervisor text notes, voice transcripts, and QA reports.
- Created seed historical dataset (`institutional_memory_seed.json`) supporting Institutional Memory testing.
- Created evaluation-only ground truth datasets (`ground_truth_dev.json`, `ground_truth_eval.json`, `ground_truth_edge_cases.json`) enforcing strict anti-cheating separation.
- Built reproducible, deterministic Python generator script in `scripts/generate_synthetic_data.py`.
- Published complete dataset specification and usage guide in `data/synthetic/README.md`.

---

## [0.4.0] - 2026-09-04

### Added
- Completed `PHASE 3 - Architecture + Data Model`.
- Published system architecture overview and authoritative source-of-truth boundaries in `docs/04-architecture/system-overview.md`.
- Specified 17 conceptual system components in `docs/04-architecture/component-architecture.md`.
- Modeled end-to-end data flow pipelines, state progression rules, and state reversibility mechanics in `docs/04-architecture/data-flow.md`.
- Formulated AI architecture, closed-vocabulary guardrail implementation (Rule 5), and 7-stage matching strategy in `docs/04-architecture/ai-architecture.md`.
- Established security architecture, role-based access matrix, and data leakage/prompt injection guardrails in `docs/04-architecture/security.md`.
- Formulated scalability evolution roadmap (Modular Monolith to Distributed Microservices) in `docs/04-architecture/scalability.md`.
- Designed conceptual data model for 19 core system entities in `docs/06-data/data-model.md`.
- Defined structural JSON schemas and enumerated state specifications in `docs/06-data/schemas.md`.
- Established schedule import boundary feasibility analysis and multi-format machine-resolvable provenance specifications in `docs/06-data/input-formats.md`.
- Specified data quality rules, idempotent ingestion design, and quarantine mechanics in `docs/06-data/data-quality.md`.

---

## [0.3.0] - 2026-09-04

### Added
- Completed `PHASE 2 - Product + Requirements`.
- Established precise product vision, positioning statement, and anti-generic-AI evaluation in `docs/02-product/product-vision.md`.
- Defined 5 detailed operational user personas and system interaction rules in `docs/02-product/personas.md`.
- Documented 5-state operational progression model (`Observed` $\rightarrow$ `Extracted` $\rightarrow$ `Matched` $\rightarrow$ `Validated` $\rightarrow$ `Projected`) and 7 end-to-end user journeys (A through G) in `docs/02-product/user-journeys.md`.
- Structured functional and product requirements catalogue (Categories A through M) in `docs/02-product/requirements.md`.
- Strict MVP scope specification and explicit out-of-scope technology evaluation matrix in `docs/02-product/mvp-scope.md`.

---

## [0.2.0] - 2026-09-04

### Added
- Completed `PHASE 1 - Problem + Domain Understanding`.
- Created problem analysis documents (`docs/01-problem/`) and domain models (`docs/03-domain/`).

---

## [0.1.0] - 2026-09-04

### Added
- Established `PHASE 0 - Foundation` repository governance.
