# Project Assumptions & Constraints

> **Governance Standard:** Explicit Assumptions Register  
> **Project:** SATYA — Oil India Limited (SIH 2026)  
> **Status:** Active Tracking  

---

## Classifications
* **`[CONFIRMED]`**: Formally established boundary condition or verified fact.
* **`[ASSUMED]`**: Technical or operational working hypothesis accepted for current phase design.
* **`[TO BE VALIDATED]`**: Open assumption requiring verification with Oil India stakeholders or domain advisors.

---

## Assumptions Register

### 1. Data Availability & Sources
* **`[CONFIRMED]` Live Oil India Proprietary Data is Unavailable:** Live connection to internal Oil India Limited enterprise databases (SAP/Primavera enterprise servers) is unavailable for hackathon prototype development due to security and confidentiality constraints.
* **`[CONFIRMED]` Synthetic & Sample Datasets Will Be Used:** Prototype validation and evaluation will rely on realistically synthesized oil and gas infrastructure project datasets (schedules, DPRs, site logs).
* **`[CONFIRMED]` Primavera/MS Project Import Format:** Primavera P6 and MS Project schedule data will initially be ingested through standard structured file exports (Primavera `.xer`, MS Project `.xml`, or standardized `.json`/`.csv` activity exports).

### 2. Technical & MVP Scope Boundaries
* **`[ASSUMED]` Production-Grade OCR is Not Required for MVP:** Deep neural OCR models for handwritten site scribbles are out of scope for the core MVP. Text extraction will assume clean PDF, digital text, or standard digital document exports.
* **`[ASSUMED]` Production-Grade Voice ASR is Not Required for MVP:** Real-time multi-dialect voice speech-to-text engines are out of scope for the core MVP engine; voice inputs will be processed using standard transcription APIs or text transcript payloads.
* **`[CONFIRMED]` SIH Prototype Scope is Controlled & Limited:** The prototype must focus on proving the end-to-end Execution Truth Layer pipeline (ingestion -> extraction -> fingerprinting -> matching -> confidence scoring -> conflict surfacing -> HITL -> actual progress) rather than full enterprise ERP integration.
* **`[CONFIRMED]` Heterogeneous Input Formats Required:** The ingestion engine must support multi-format field observations (textual DPRs, tabular daily logs, structured form data, voice transcripts).
* **`[CONFIRMED]` L5/L6 Schedule Activities as Primary Target:** Matching engine targets L5/L6 schedule activities (work-package / task execution level) as the primary alignment target.

### 3. Operational & Domain Factors
* **`[TO BE VALIDATED]` Oil India WBS Taxonomy Standards:** Specific internal WBS code naming conventions used across Oil India pipeline and drilling projects require domain validation during Phase 1.
* **`[TO BE VALIDATED]` Standard DPR Template Variations:** The degree of variation across contractor DPR templates in different Oil India assets (Assam, Rajasthan, Offshore) needs domain sample mapping.
* **`[ASSUMED]` Planner Availability for HITL:** Project planners will dedicate periodic review cycles to evaluate low-confidence match queues and resolve flagged conflicts.
