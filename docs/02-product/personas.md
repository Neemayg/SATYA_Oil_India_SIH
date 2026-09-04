# Operational User Personas & System Interaction Specifications

> **Document Type:** User Persona & Role Specification  
> **Governance Status:** Phase 2 Deliverable  
> **Project:** SATYA — Oil India Limited (SIH 2026)  

---

## 1. Persona Matrix Overview

SATYA serves 5 primary operational user personas across the Oil India project execution lifecycle.

---

## 2. Detailed Persona Specifications

### 2.1 Persona 1: Senior Planning & Scheduling Engineer (PMO Lead)
* **Name / Title:** Planning & Scheduling Engineer
* **Entity:** Oil India Project Management Office (PMO)
* **Core Responsibilities:** Creates and maintains L1–L6 Primavera P6 project schedules, incorporates actual progress, tracks critical path variance, issues weekly/monthly S-curves.
* **Information Created:** Baseline schedules, WBS structures, activity target quantities, Primavera `.xer` files, progress transmittals.
* **Information Consumed:** Contractor DPRs, site inspection reports, field observation logs, actual start/finish dates, physical percentage complete claims.
* **Current Pain Points:** Spends 70% of time reading unstructured DPR text, guessing P6 activity matches, manually typing progress numbers, and resolving audit disputes over unverified claims.
* **SATYA Interaction:** Uses the **Human-in-the-Loop (HITL) Validation Interface** to review flagged low-confidence matches, inspect evidence provenance, resolve detected conflicts, and approve schedule projections into Primavera P6.
* **Decisions Made:** Resolves ambiguous activity matches, approves/rejects contested progress claims, overrides invalid AI candidates, re-baselines schedule logic.
* **Information Needed to Trust:** Raw source snippet, byte offset, file origin, attached QA/photo evidence, confidence score factor breakdown, conflict flags.
* **What SATYA MUST Automate:** Event extraction from DPRs, candidate matching against Activity Fingerprints, confidence scoring, conflict surfacing, evidence linkage, draft schedule projection generation.
* **What SATYA MUST NOT Decide:** Never automatically overwrite Primavera baseline logic, never force a low-confidence match ($\text{Confidence} < \theta$), never invent Activity IDs.
* **Status:** `[CONFIRMED]` Core target user for SATYA HITL interface.

---

### 2.2 Persona 2: Resident Site Engineer / Field Supervisor
* **Name / Title:** Field / Resident Site Engineer
* **Entity:** Oil India Field Operations
* **Core Responsibilities:** Monitors daily physical execution across remote site spreads (pipeline spreads, well-pads, GGS units), verifies contractor performance, ensures safety/quality adherence.
* **Information Created:** Daily site logs, field verification notes, geotagged site photographs, site inspection requests, operational stoppage records.
* **Information Consumed:** Approved engineering drawings, daily execution targets, EPC contractor DPR submissions.
* **Current Pain Points:** High administrative burden; forced to re-key field observations into static Excel templates; lack of immediate feedback on whether field notes matched schedule targets.
* **SATYA Interaction:** Submits raw field observations via text notes, voice memos, site photos, or digital field form entries without needing Primavera Activity IDs.
* **Decisions Made:** Verifies whether physical work claimed by contractor actually occurred on site.
* **Information Needed to Trust:** Simple acknowledgment that field log was ingested, linked to correct site section, and queued for planner review.
* **What SATYA MUST Automate:** Parsing informal site text/voice transcripts, extracting location/quantity entities, auto-linking attached photos to execution events.
* **What SATYA MUST NOT Decide:** Never override site engineer verification sign-offs on physical work execution.
* **Status:** `[CONFIRMED]`

---

### 2.3 Persona 3: EPC Contractor Site Manager / Reporting Clerk
* **Name / Title:** EPC Contractor Project Engineer
* **Entity:** External EPC Contractor Firm
* **Core Responsibilities:** Executes physical construction work (trenching, stringing, welding, civil foundations), compiles daily progress reports (DPRs), submits interim billing claims.
* **Information Created:** Daily Progress Reports (Excel/PDF), joint measurement sheets, material receipt tickets, shift progress logs.
* **Information Consumed:** Approved work packages, issued-for-construction drawings, baseline target dates.
* **Current Pain Points:** Interim billing claims held up for weeks due to manual sign-off disputes; lack of transparent evidence tracking.
* **SATYA Interaction:** Submits daily DPR files via file upload or transmittal interface.
* **Decisions Made:** Reports daily manpower, machinery usage, and physical quantities executed per section.
* **Information Needed to Trust:** Transparent status view showing which reported quantities were matched, verified with evidence, and accepted into schedule actuals.
* **What SATYA MUST Automate:** Extracting multi-tab Excel DPR entries, mapping micro-quantities to L5 activities, flagging missing required evidence attachments.
* **What SATYA MUST NOT Decide:** Never modify raw contractor DPR submission content.
* **Status:** `[REASONABLE DOMAIN ASSUMPTION]`

---

### 2.4 Persona 4: Third-Party Inspection Agency (TPIA) / QA Supervisor
* **Name / Title:** QA/QC & TPIA Quality Inspector
* **Entity:** Independent QA Agency / Oil India Quality Cell
* **Core Responsibilities:** Performs non-destructive testing (NDT), radiographic inspections, hydrostatic pressure tests, structural concrete cube tests; issues clearance certificates or Non-Conformance Reports (NCRs).
* **Information Created:** NDT clearance reports, Radiography test sheets, Hydrotest certificates, NCR forms, Punch lists.
* **Information Consumed:** Inspection call requests, welding joint logs, material test certificates.
* **Current Pain Points:** Quality certificates remain in separate binders or folders, detached from progress reporting, allowing unverified work to be reported as 100% complete.
* **SATYA Interaction:** Ingests inspection certificates and test reports; SATYA automatically cross-links certificates to corresponding execution events as verifying evidence.
* **Decisions Made:** Certifies whether executed work satisfies Oil India engineering standards.
* **Information Needed to Trust:** Verified link between QA certificate ID and specific pipeline joint / foundation activity ID.
* **What SATYA MUST Automate:** Extracting test status (Pass/Fail) and joint/chainage references from QA certificates; flagging QA failures as schedule conflict flags.
* **What SATYA MUST NOT Decide:** Never mark a QA-failed activity as complete.
* **Status:** `[REASONABLE DOMAIN ASSUMPTION]`

---

### 2.5 Persona 5: Project Director / Executive PMO Leadership
* **Name / Title:** Project Director / Executive Director (Projects)
* **Entity:** Oil India Executive Leadership
* **Core Responsibilities:** Oversees portfolio health, allocates capital, manages stakeholder milestone commitments, conducts executive progress reviews.
* **Information Created:** Executive directives, milestone milestone targets, capital budget approvals.
* **Information Consumed:** Executive summary S-curves, milestone completion forecasts, delay risk alerts, audit compliance logs.
* **Current Pain Points:** Distrusts current S-curves due to historical late-stage delay surprises ("90% complete syndrome"); lacks audit-proof evidence backing claimed percentage progress.
* **SATYA Interaction:** Views high-level executive dashboards showing evidence-backed progress percentage, active conflict flags, evidence-gap alerts, and institutional memory analytics.
* **Decisions Made:** Approves baseline scope changes, contractual extension of time (EOT) claims, resource re-allocations.
* **Information Needed to Trust:** Audit-proof provenance backing every progress percentage number (ability to drill down from L1 milestone to raw DPR photo proof).
* **What SATYA MUST Automate:** Aggregating trusted L5 execution events up to L1-L3 milestone S-curves; calculating evidence completeness metrics.
* **What SATYA MUST NOT Decide:** Never alter executive milestone targets or baseline completion commitments.
* **Status:** `[CONFIRMED]`
