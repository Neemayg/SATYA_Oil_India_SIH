# System & Domain Glossary

> **Document Type:** Project Taxonomy & Definitions  
> **Project:** SATYA — Oil India Limited (SIH 2026)  
> **Status:** Canonical Definitions  

---

## Terms & Definitions

### Schedule Hierarchy (L1 - L6)
* **L1 (Executive Summary Schedule):** High-level project portfolio schedule showing major project phases and key key-result dates for executive leadership.
* **L2 (Management Summary Schedule):** High-level operational schedule breaking down the project by major facilities, fields, or plants.
* **L3 (Control Schedule):** Overall project master schedule used by project directors to monitor contract packages and major milestones.
* **L4 (Execution Schedule):** Detailed package-level schedule used by project engineers and EPC contractors to coordinate discipline activities.
* **L5 (Work Package Schedule):** Highly detailed activity schedule defining discrete physical work items (e.g., specific pipe spools, foundation pours).
* **L6 (Step/Task Schedule):** Operational field-level task breakdown defining daily shift tasks, crew assignments, and equipment steps.

### Project Management Terms
* **WBS (Work Breakdown Structure):** A hierarchical decomposition of total project scope into manageable, deliverable-oriented work packages.
* **Baseline:** The approved, frozen version of a project schedule (scope, start/finish dates, resources) against which actual execution performance is measured.
* **Activity:** A discrete work package in a schedule with a defined scope, duration, start/finish dates, and resource assignments.
* **Milestone:** A zero-duration schedule marker representing a significant event, approval, or completion point in the project lifecycle.
* **DPR (Daily Progress Report):** A standard site document compiled by contractors or field engineers detailing daily work completed, manpower, equipment usage, and delays.
* **PMIS (Project Management Information System):** The software suite (e.g., Primavera P6, MS Project) used to store and manage formal project schedules.
* **Actual Start:** The verified calendar date on which physical execution of an activity commenced.
* **Actual Finish:** The verified calendar date on which physical execution of an activity was 100% completed.

### SATYA Core Engine Concepts
* **Execution Event:** A structured, normalized data record extracted from a field observation representing a physical work occurrence (e.g., "120m trenching dug at Section A on 2026-09-04").
* **Execution Event Ledger:** An append-only, immutable database storing raw field inputs and extracted Execution Events with full audit metadata.
* **Activity Fingerprint:** A multi-dimensional feature signature generated for each schedule activity, encapsulating semantic, structural, spatial, and temporal context.
* **Evidence:** Verifiable physical or documentary corroboration attached to a field observation (e.g., QA inspection certificate, geotagged site photo, material dispatch slip).
* **Provenance:** Complete origin tracking metadata for an event, including raw source document, byte offset, timestamp, author, and ingestion log.
* **Semantic Matching:** Natural language processing techniques measuring contextual meaning alignment between field text descriptions and schedule activity signatures.
* **Fuzzy Matching:** String distance algorithms (e.g., Levenshtein, Token Sort) measuring lexical similarity between site terminology and schedule labels.
* **Embedding:** High-dimensional vector representation of text captures semantic intent for vector similarity search.
* **LLM (Large Language Model):** Artificial intelligence language model used for entity extraction, context parsing, and reasoning trace generation under strict guardrails.
* **Confidence Score:** A normalized value $[0.0, 1.0]$ representing the system's mathematical certainty that a specific Execution Event maps to a specific schedule Activity.
* **Human-in-the-Loop (HITL):** A governance mechanism routing low-confidence or disputed AI matches to a human planner for explicit review and decision.
* **Conflict:** A detected contradiction between two or more field observations or between a field observation and physical schedule logic.
* **Evidence Gap:** An active schedule activity within its planned execution window for which no field observations or evidence have been recorded.
* **Granularity Mismatch:** The structural discrepancy between micro-level daily field logs and higher-level L5/L6 baseline schedule activities.
* **Institutional Memory:** A persistent historical knowledge store capturing actual execution rates, delay root-causes, local site terminology, and planner correction histories to inform future project planning.
