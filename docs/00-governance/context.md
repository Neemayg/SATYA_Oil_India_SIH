# Project Context & Problem Domain

> **Document Status:** Canonical Truth  
> **Governance Level:** Level 0 — System Context  
> **Project:** SATYA (Schedule-Aligned Truth & Yield Analytics) — Oil India Limited (SIH 2026)  

---

## 1. Executive Summary & SIH 2026 Context

This project is developed for **Smart India Hackathon (SIH) 2026** addressing a core operational challenge faced by **Oil India Limited (OIL)** in major capital project execution (e.g., pipeline laying, drilling rig setup, refinery unit construction, gas gathering stations, and civil infrastructure).

Mega-projects in upstream oil and gas involve complex multi-tiered schedules (L1 through L6 Primavera P6 / MS Project plans) spanning thousands of activities across remote geographical locations.

---

## 2. Problem Background & Core Challenge

### 2.1 The Operational Reality
In capital projects, project management offices (PMOs) maintain detailed L5/L6 project schedules. However, actual site progress is reported through fragmented, unstructured, and heterogeneous field channels:
* Daily Progress Reports (DPRs) submitted in PDF/Excel formats
* Site engineer voice memos and text WhatsApp/email updates
* Contractor milestone claims and inspection requests
* Physical site logs, material movement tickets, and site photographs

### 2.2 The Core Problem
1. **Semantic & Structural Disconnect:** Field execution operates at a micro-level (e.g., "completed 150m trenching at Section B, ROW clearing blocked by stream"), whereas PMIS schedules operate at L5/L6 activity levels (e.g., `ACT-3490: Mainline Pipeline Trenching - Km 12 to Km 18`). Mapping these manually is slow, error-prone, and subjective.
2. **Unverified Progress & Optimism Bias:** Progress reports are often accepted without verifiable cross-evidence, leading to sudden late-stage schedule slippage ("90% complete syndrome").
3. **Contradictions & Evidence Gaps:** Different field sources (e.g., Civil Contractor vs. Quality Inspector) frequently submit conflicting status reports that are obscured during manual aggregation.
4. **Loss of Field Intelligence:** Planner overrides, actual execution rates, delay causes, and local contractor terminology are lost in email threads instead of being institutionalized.

---

## 3. Target Users

1. **Project Managers & PMO Leads:** Seeking accurate, evidence-backed actual progress and trustworthy forecast completion dates.
2. **Planning & Scheduling Engineers:** Requiring automated, schedule-aware matching of field logs to Primavera L5/L6 activities without manual spreadsheet mapping.
3. **Site Engineers & Field Supervisors:** Reporting daily progress through natural, heterogeneous inputs without being burdened by complex scheduling software.
4. **Oil India Executive Management:** Requiring high-integrity audit trails and early warning signals of schedule divergence.

---

## 4. Core Solution: The Execution Truth Layer (ETL)

SATYA introduces an **Execution Truth Layer** positioned between field execution observations and the formal L5/L6 project schedule.

```
+-----------------------------------------------------------------------+
|                       FIELD OBSERVATIONS                              |
|   (DPRs, Voice Notes, Site Photos, Inspector Logs, Contractor Memos)   |
+-----------------------------------------------------------------------+
                                   |
                                   v
+-----------------------------------------------------------------------+
|                    EXECUTION EVENT LEDGER (Raw)                       |
|          (Immutable, Provenance-Tracked Raw Execution Events)           |
+-----------------------------------------------------------------------+
                                   |
                                   v
+-----------------------------------------------------------------------+
|                   EXECUTION TRUTH LAYER (SATYA)                       |
|                                                                       |
|   1. Activity Fingerprinting (Semantic + Structural + Temporal)       |
|   2. Schedule-Aware Matching Engine (Maps events to L5/L6)            |
|   3. Multi-Modal Evidence & Confidence Verification                   |
|   4. Conflict & Evidence-Gap Detection Engine                         |
+-----------------------------------------------------------------------+
                                   |
                   +---------------+---------------+
                   |                               |
       (High Confidence Match)          (Low Confidence / Conflict)
                   |                               |
                   v                               v
+------------------------------------+   +------------------------------+
|     TRUSTED ACTUAL PROGRESS        |   |    HUMAN-IN-THE-LOOP (HITL)  |
|  (Verified Start/Finish/Quantity)  |   |    PLANNER VALIDATION        |
+------------------------------------+   +------------------------------+
                   |                               |
                   +---------------+---------------+
                                   |
                                   v
+-----------------------------------------------------------------------+
|                      INSTITUTIONAL MEMORY                             |
|  (Actual Durations, Productivity Rates, Terminology, Planner Rules)   |
+-----------------------------------------------------------------------+
```

---

## 5. Key Architecture Concepts

### 5.1 Execution Event Ledger
An append-only, immutable ledger storing structured `ExecutionEvents` derived from field inputs. Every event retains original source text, file offset, timestamp, location tag, and author metadata (provenance).

### 5.2 Activity Fingerprint
A multi-dimensional context signature for every L5/L6 schedule activity, combining:
* **Semantic Context:** Activity name, description, WBS path, resource tags, discipline keywords.
* **Structural Context:** Predecessor/successor dependencies, WBS parent/child relationships, physical area/zone.
* **Temporal Context:** Planned start date, planned finish date, early/late bounds, active execution window.

### 5.3 Schedule-Aware Matching
A multi-layered matching engine that evaluates candidate Execution Events against Activity Fingerprints using semantic similarity, temporal alignment, and structural sanity rules.

### 5.4 Evidence-Backed Progress & Confidence
Progress is assigned a normalized confidence score $[0.0, 1.0]$. High progress percentages backed by corroborating evidence (e.g., photo + inspection log) score high; single unverified claims score low.

### 5.5 Conflict & Evidence-Gap Detection
* **Conflict Detection:** Identifies contradictory observations (e.g., DPR reports 80% pipe laying complete while inspection report states trenching failed QA).
* **Evidence-Gap Detection:** Identifies critical active schedule activities with zero reported field observations.

### 5.6 Human-in-the-Loop (HITL)
An interactive planner verification interface where ambiguous or conflicting matches are presented with complete evidence context and reasoning traces for human resolution.

### 5.7 Institutional Memory
A growing repository of historical execution metrics, real-world task durations, contractor productivity factors, and recorded planner corrections to refine future project scheduling and automated matching.

---

## 6. Functional Scope Matrix: Requirements vs. SATYA Differentiation

| Dimension | What the SIH Problem Statement Requires | What SATYA Adds as Differentiation |
| :--- | :--- | :--- |
| **Input Processing** | Parsing DPR documents and spreadsheets into status updates. | Multi-modal ingestion into an **Immutable Execution Event Ledger** with strict provenance tracking. |
| **Schedule Alignment** | Basic string text matching between DPR descriptions and schedule task names. | **Schedule-Aware Activity Fingerprinting** combining semantic embeddings, WBS structural topology, spatial constraints, and temporal windows. |
| **Progress Calculation** | Extracting reported percentage numbers and updating progress bars. | **Evidence-Backed Verification** calculating explicit multi-factor confidence scores ($[0.0, 1.0]$). |
| **Discrepancy Handling** | Displaying delay alerts or overdue task lists. | Active **Conflict Detection** (contradictory reports) and **Evidence-Gap Detection** (unreported active tasks). |
| **AI Role** | Black-box LLM generating status summaries or answers. | **Explainable AI Guardrails** with strict HITL workflow; LLM cannot invent activity IDs or silently alter baselines. |
| **Long-Term Value** | Disposable status reports per project. | **Institutional Memory** capturing true execution rates, delay causes, and planner corrections for future planning intelligence. |
