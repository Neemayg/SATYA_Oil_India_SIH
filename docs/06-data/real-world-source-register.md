# Real-World Data Source Register

> **Document Type:** Data Reconnaissance Source Register  
> **Governance Status:** Phase 4.5 Deliverable  
> **Project:** SATYA — Oil India Limited (SIH 2026)  
> **Licensing Constraint:** Reference & Benchmark Evaluation Only; Zero Redistribution of Proprietary Content.  

---

## 1. Source Register Overview

This register logs publicly accessible project execution and progress monitoring data sources investigated during Phase 4.5. Every source is classified into 1 of 4 standard categories:

* **`[BENCHMARK_CANDIDATE]`**: Open public project execution data suitable for processing as a robustness test benchmark.
* **`[REFERENCE_MATERIAL]`**: Useful for domain terminology, reporting structure, or language analysis, but not as benchmark ground truth.
* **`[MANUALLY_LABELABLE]`**: Public text material where a small subset can be manually annotated to create gold evaluation cases.
* **`[UNSUITABLE]`**: Technical or domain data (e.g., sensor streams, drilling telemetry, price indices) that does not represent SATYA's schedule-matching problem.

---

## 2. Investigated Source Register Matrix

| Source ID | Source Name & Publisher | Source Type & Region | Key Content & Fields Available | Schedule Linkage? | Language Style | Licensing & Access | Classification & Suitability Rating |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **SRC-RW-01** | **MoSPI PAIMANA / OCMS Monthly Flash Reports** *(Ministry of Statistics & PI, Govt of India)* | Government Infrastructure Portal (India) | Sectoral milestone dates, revised cost, physical % complete, delay root cause notes. | L1/L2 High Level Only | Formal administrative summaries | Open Public Release (Govt of India Portal) | `[REFERENCE_MATERIAL]` (Rating: High for delay causes & L1/L2 terms) |
| **SRC-RW-02** | **USACE Resident Management System (RMS) QC Daily Reports** *(US Army Corps of Engineers)* | Federal Construction Log Format (USA) | Shift notes, equipment hours, quantity installed, QA/QC inspection sign-offs, weather delays. | Yes (RMS / Primavera P6 Link) | Realistic human site supervisor shorthand | Public Domain (US Federal Standards) | `[BENCHMARK_CANDIDATE]` (Rating: High for daily site log structure) |
| **SRC-RW-03** | **FIDIC Red/Yellow Book Daily Site Register Templates** *(FIDIC International)* | EPC Contract Transmittal Standard (Global) | Contractor daily progress entries, manpower, equipment downtime, site instruction notes. | Indirect | Standard EPC contractor reporting language | Open Reference Template | `[REFERENCE_MATERIAL]` (Rating: Medium for contract transmittal structures) |
| **SRC-RW-04** | **Academic NLP Construction Progress Text Corpus** *(Journal of Construction Eng & Mgmt / Public Datasets)* | Academic Dataset (Global) | Annotated site diary sentences, entity tags (action, location, quantity, material). | Partial | Natural, messy human site diary entries | Academic Open Data (CC-BY 4.0) | `[MANUALLY_LABELABLE]` (Rating: High for NLP entity extraction benchmarks) |
| **SRC-RW-05** | **Public Cross-Country Pipeline EIA & EMP Monitoring Reports** *(State Environmental Boards)* | Environmental Infrastructure Logs (India) | Chainage-wise ROW clearing, trenching, stream crossing clearance, restoration logs. | Chainage Based | Formal technical engineering reports | Public Government Transcripts | `[REFERENCE_MATERIAL]` (Rating: High for pipeline chainage & environmental terms) |
| **SRC-RW-06** | **Volve Oil Field Production & Well Telemetry Dataset** *(Equinor Public Release)* | Production & Reservoir Telemetry (Norway) | Daily oil/gas production volumes, wellhead pressure, choke size, temperature. | **No** | Sensor numerical telemetry | Open Data License (Equinor) | `[UNSUITABLE]` (Rating: Unsuitable — Telemetry, not execution progress) |
| **SRC-RW-07** | **Rig Activity & Drilling Sensor Time-Series** *(OpenDT / Society of Petroleum Engineers)* | Rig Sensor Telemetry (Global) | Rate of penetration (ROP), weight on bit (WOB), mud flow, pump pressure. | **No** | Sensor numerical streams | Public Research Data | `[UNSUITABLE]` (Rating: Unsuitable — Drilling dynamics, not schedule progress) |
