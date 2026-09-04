# SATYA System Documentation Index

> **Project:** SATYA (Schedule-Aligned Truth & Yield Analytics) — Oil India Limited (SIH 2026)  
> **Current Status:** PHASE 0 — Foundation Established  

---

## 1. Documentation Structure & Map

The documentation repository is organized into distinct numerical domains reflecting system governance, specifications, core engines, and operational details:

```
docs/
├── README.md                      <-- (This Index)
├── 00-governance/                 <-- Non-negotiable rules, context, ADRs, assumptions, phases, glossary
│   ├── context.md
│   ├── rules.md
│   ├── decisions.md
│   ├── assumptions.md
│   ├── glossary.md
│   └── development-phases.md
├── 01-problem/                    <-- Detailed problem background & domain breakdown
├── 02-product/                    <-- Product requirements (PRD) & user stories
├── 03-domain/                     <-- Oil India specific domain models & Primavera P6 structures
├── 04-architecture/               <-- System architecture & data flow diagrams
├── 05-core-engines/               <-- Algorithms, matching specs, & conflict engine design
├── 06-data/                       <-- Event schemas, database models, & provenance spec
├── 07-ai/                         <-- Prompt engineering, guardrails, & embedding specs
├── 08-api/                        <-- REST/gRPC API contracts & payload specs
├── 09-frontend/                   <-- UX wireframes, HITL interface specs, & component specs
├── 10-testing/                    <-- Test strategy, evaluation benchmarks, & synthetic dataset specs
└── 11-sih/                        <-- SIH 2026 submission artifacts, slides, & demo scripts
```

---

## 2. Directory Purpose & Authoritative Source Table

| Topic / Category | Directory Path | Authoritative Source Document | Purpose |
| :--- | :--- | :--- | :--- |
| **Governance & Rules** | `docs/00-governance/` | [`rules.md`](file:///Users/neemaysmac/Desktop/OIL_India_SIH/docs/00-governance/rules.md) | Non-negotiable system engineering rules and constraints. |
| **System Context** | `docs/00-governance/` | [`context.md`](file:///Users/neemaysmac/Desktop/OIL_India_SIH/docs/00-governance/context.md) | Canonical problem statement, target users, and ETL concept. |
| **Architectural Decisions** | `docs/00-governance/` | [`decisions.md`](file:///Users/neemaysmac/Desktop/OIL_India_SIH/docs/00-governance/decisions.md) | ADR log for approved system architectural choices. |
| **Assumptions Register** | `docs/00-governance/` | [`assumptions.md`](file:///Users/neemaysmac/Desktop/OIL_India_SIH/docs/00-governance/assumptions.md) | Confirmed and assumed operational hypotheses. |
| **Development Lifecycle** | `docs/00-governance/` | [`development-phases.md`](file:///Users/neemaysmac/Desktop/OIL_India_SIH/docs/00-governance/development-phases.md) | Phase definitions (Phase 0 to 16) and exit criteria. |
| **Terminology** | `docs/00-governance/` | [`glossary.md`](file:///Users/neemaysmac/Desktop/OIL_India_SIH/docs/00-governance/glossary.md) | Standard project definitions and Oil India domain terms. |
| **Problem Specifications** | `docs/01-problem/` | `01-problem/` documents | Detailed breakdown of Oil India field challenges. |
| **Product Requirements** | `docs/02-product/` | `02-product/` documents | Feature scope, persona stories, and MVP boundaries. |
| **System Architecture** | `docs/04-architecture/` | `04-architecture/` documents | Component design, data pipelines, and security specs. |
| **Core Engines** | `docs/05-core-engines/` | `05-core-engines/` documents | Algorithms for Fingerprinting, Matching, Confidence, & Conflicts. |

---

## 3. Development Phases Summary

SATYA's lifecycle is strictly governed across 17 controlled phases (Phase 0 through Phase 16). Full phase controls, inputs, outputs, and exit criteria are specified in [`docs/00-governance/development-phases.md`](file:///Users/neemaysmac/Desktop/OIL_India_SIH/docs/00-governance/development-phases.md).

* **Current Active Phase:** `PHASE 0 - Foundation`
* **Next Phase:** `PHASE 1 - Problem + Domain Understanding`

---

## 4. Documentation Update Policy

1. **Docs-First & Sync Rule:** Any proposal or pull request modifying data models, matching logic, or user workflows must update the corresponding file in `docs/` within the same pull request.
2. **ADR Requirement:** New architectural decisions must be submitted as a new ADR entry in [`docs/00-governance/decisions.md`](file:///Users/neemaysmac/Desktop/OIL_India_SIH/docs/00-governance/decisions.md) and approved before implementation code is written.
3. **No Drift Allowed:** Code that deviates from documentation is considered buggy and non-compliant.
