# SATYA

> **Working Expansion:** Schedule-Aligned Truth & Yield Analytics *(Provisional Name)*  
> **Target Problem:** Smart India Hackathon 2026 — Oil India Limited  
> **Current Status:** `PHASE 4 — SYNTHETIC DATA ENGINEERING` (Completed — Implementation code has NOT started)  

---

## 1. Project Overview

**SATYA** is an evidence-backed **Execution Truth Layer** designed to bridge the operational gap between unstructured field execution observations (Daily Progress Reports, site notes, voice logs, inspection certificates) and high-level L5/L6 Primavera P6 / MS Project schedules for Oil India Limited.

Rather than acting as a generic AI chatbot, SATYA converts heterogeneous field observations into structured Execution Events, grounds them against multi-dimensional Activity Fingerprints, calculates explicit multi-factor confidence scores, surfaces conflicts and evidence gaps, and routes low-confidence matches to a Human-in-the-Loop planner queue before producing audit-trusted actual schedule progress.

---

## 2. Problem & Domain Context

In mega-projects undertaken by Oil India Limited (such as cross-country pipeline construction, gas gathering station commissioning, and drilling rig site preparation), progress reporting suffers from:
* Semantic and structural disconnects between micro-level field tasks and macro-level L5/L6 schedule activities.
* Unverified progress claims and subjective reporting leading to sudden late-stage schedule delay surprises.
* Hidden contradictions between contractor claims and field inspection logs.
* Loss of real-world execution metrics and contractor productivity intelligence.

---

## 3. Core Product Concept: Execution Truth Layer (ETL)

SATYA introduces a multi-tier execution intelligence architecture:
1. **Immutable Execution Event Ledger:** Stores raw inputs and extracted events with 100% audit provenance.
2. **Activity Fingerprinting:** Multi-dimensional semantic + structural + temporal grounding of Primavera L5/L6 schedule activities.
3. **Schedule-Aware Matching Engine:** Constrained, deterministic-boosted alignment supporting explicit `UNMATCHED` outputs.
4. **Multi-Modal Evidence & Confidence Scoring:** Mathematical verification producing explicit $[0.0, 1.0]$ confidence scores.
5. **Conflict & Gap Engine:** Surfaces contradictory field claims and unreported active schedule tasks.
6. **Human-in-the-Loop (HITL) Workflow:** Interactive planner validation interface for low-confidence or disputed events.
7. **Institutional Memory:** Long-term repository capturing true execution rates, delay causes, and planner correction histories.

---

## 4. Current Repository Status & Implementation Statement

> **IMPORTANT NOTICE:**  
> This repository is currently in **`PHASE 0 - FOUNDATION`**.  
> **No application code, frontend/backend APIs, database tables, or AI matching logic have been implemented yet.**  
> The repository currently contains exclusively governance frameworks, problem context, engineering rules, architectural decision records (ADRs), and phase control controls.

---

## 5. Planned Development Phases

Development strictly follows a 17-phase lifecycle defined in [`docs/00-governance/development-phases.md`](file:///Users/neemaysmac/Desktop/OIL_India_SIH/docs/00-governance/development-phases.md):

* **PHASE 0:** Foundation *(Active)*
* **PHASE 1:** Problem + Domain Understanding
* **PHASE 2:** Product + Requirements
* **PHASE 3:** Architecture + Data Model
* **PHASE 4:** Synthetic Data Specification & Generation
* **PHASE 5:** Execution Event Ingestion Pipeline
* **PHASE 6:** Activity Fingerprinting Engine
* **PHASE 7:** Schedule-Aware Matching Engine
* **PHASE 8:** Evidence + Confidence + Conflict Engine
* **PHASE 9:** Human Validation (HITL) Workflow
* **PHASE 10:** Actual Progress + Schedule Projection Engine
* **PHASE 11:** Backend Application Services
* **PHASE 12:** Frontend Planner Dashboard & HITL Interface
* **PHASE 13:** Time Agent (Proactive Schedule Monitoring)
* **PHASE 14:** Analytics + Institutional Memory Store
* **PHASE 15:** Comprehensive Testing & Benchmark Evaluation
* **PHASE 16:** SIH Demo & Final Presentation Packaging

---

## 6. Repository Documentation Location

All project specifications and governance documents are situated within the `docs/` directory:

* **[Master AI Instructions](file:///Users/neemaysmac/Desktop/OIL_India_SIH/AGENTS.md):** Rules for AI coding agents.
* **[Documentation Index](file:///Users/neemaysmac/Desktop/OIL_India_SIH/docs/README.md):** Directory map and authoritative document guide.
* **[System Context](file:///Users/neemaysmac/Desktop/OIL_India_SIH/docs/00-governance/context.md):** Detailed problem statement, target users, and ETL architecture.
* **[System Rules](file:///Users/neemaysmac/Desktop/OIL_India_SIH/docs/00-governance/rules.md):** 20 non-negotiable engineering rules.
* **[Architectural Decisions](file:///Users/neemaysmac/Desktop/OIL_India_SIH/docs/00-governance/decisions.md):** Formal ADR log (DEC-001 through DEC-004).
* **[Assumptions Register](file:///Users/neemaysmac/Desktop/OIL_India_SIH/docs/00-governance/assumptions.md):** Categorized system assumptions.
* **[System Glossary](file:///Users/neemaysmac/Desktop/OIL_India_SIH/docs/00-governance/glossary.md):** Project and Primavera/Oil India domain definitions.
