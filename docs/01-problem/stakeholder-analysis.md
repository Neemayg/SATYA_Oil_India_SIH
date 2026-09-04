# Stakeholder Analysis & Operational Persona Mapping

> **Document Type:** Operational Stakeholder Analysis  
> **Governance Status:** Phase 1 Deliverable  
> **Project:** SATYA — Oil India Limited (SIH 2026)  

---

## 1. Executive Summary

Executing capital infrastructure projects at Oil India Limited involves multiple internal departments and external entities. Understanding their distinct roles, input formats, reporting friction, and incentives is essential for designing SATYA's **Execution Truth Layer** and Human-in-the-Loop (HITL) workflows.

---

## 2. Key Stakeholder Personas Matrix

| Persona / Role | Organizational Entity | Primary Responsibility | Input Artifacts Generated | Output Artifacts Consumed | Primary Pain Points |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Planning & Scheduling Engineer** | Oil India PMO | Maintains L1-L6 Primavera P6 baseline, updates progress, forecasts completion dates. | Baseline schedule, WBS dictionary, S-Curves, progress reports. | DPRs, contractor claims, inspection logs. | Spent 60%+ time manually reading DPR text and guessing P6 activity mappings. |
| **Field / Resident Site Engineer** | Oil India Field Ops | Monitors site work, verifies contractor execution, ensures safety compliance. | Site logs, inspection requests, daily field notes, site photos. | Approved DPRs, daily execution targets. | Burdened by administrative paperwork; no easy way to record observations naturally. |
| **EPC Contractor Site Manager** | External EPC Firm | Executes physical construction (trenching, welding, civil, electrical). | Daily Progress Reports (DPRs), measurement sheets, invoice claims. | Issued drawings, baseline schedules, work orders. | Progress claims delayed due to manual verification disputes and paperwork backlogs. |
| **Third-Party Inspection Agency (TPIA)** | Independent QA Agency | Conducts non-destructive testing (NDT), hydrostatic tests, QA certification. | Quality certificates, NDT report sheets, non-conformance reports (NCR). | Inspection calls, test procedures. | QA certificates managed separately from progress reports; no automated cross-linkage. |
| **Project Director / Executive Mgmt** | Oil India Leadership | Overlooks portfolio health, capital allocation, milestone compliance. | Executive directives, milestone approvals. | L1/L2 summary dashboards, delay risk reports, milestone forecasts. | Distrusts current progress numbers due to late delay surprises ("90% syndrome"). |

---

## 3. Stakeholder Ecosystem & Information Flow

```
   [EPC Contractor] ----------(Submits DPRs & Logs)----------> [Site Engineer]
          |                                                         |
          | (Physical Work)                                         | (Verifies & Forwards)
          v                                                         v
   [Physical Site] <--(Inspects & Tests)-- [TPIA Inspector] ---> [Oil India PMO Planner]
                                                                    |
                                                                    | (Manually updates P6)
                                                                    v
                                                         [Executive Leadership]
```

### Detailed Stakeholder Specifications

### 3.1 Planning & Scheduling Engineer (PMO)
* **Status:** `[CONFIRMED]` Core target user for SATYA HITL interface.
* **Incentives:** Accurate schedule forecasts, zero audit non-conformances, early identification of critical path delays.
* **SATYA Interaction:** Uses SATYA HITL interface to review flagged low-confidence matches, resolve contradictory field observations, view evidence provenance, and approve schedule projections into Primavera P6.

### 3.2 Field / Resident Site Engineer (Oil India)
* **Status:** `[CONFIRMED]` Key field observation provider.
* **Incentives:** Timely project execution, strict quality compliance, minimal administrative overhead.
* **SATYA Interaction:** Submits observations via heterogeneous text notes, voice memos, digital forms, or structured DPR attachments without needing Primavera Activity IDs.

### 3.3 EPC Contractor Site Manager
* **Status:** `[REASONABLE DOMAIN ASSUMPTION]` External stakeholder generating primary daily DPRs.
* **Incentives:** Maximizing billable progress, securing interim payments, avoiding delay penalties.
* **SATYA Interaction:** Submits standard DPR spreadsheets/files; benefits from transparent evidence verification that reduces billing dispute cycles.

### 3.4 Third-Party Inspection Agency (TPIA) / Quality Supervisor
* **Status:** `[REASONABLE DOMAIN ASSUMPTION]` Independent validator.
* **Incentives:** Strict quality assurance, zero compliance failures, independent evidence reporting.
* **SATYA Interaction:** Uploads inspection certificates, NDT test logs, and quality clearance forms which SATYA automatically cross-links to execution events as verifying evidence.

### 3.5 Executive Leadership / Project Director
* **Status:** `[CONFIRMED]` High-level consumer of execution intelligence.
* **Incentives:** On-time commissioning, risk mitigation, audit-proof project governance.
* **SATYA Interaction:** Views trusted S-Curves, evidence-backed progress percentage, active conflict flags, and institutional memory analytics.

---

## 4. Operational Friction & Mapping Disconnects

```
   CONTRACTOR FIELD REPORT                    PRIMAVERA P6 BASELINE
   "Completed 150m ROW clearing                ACT-1040: ROW Clearing & Grading
   and grubbing at Chainage 14+200             WBS: 1.2.4.1 Mainline Pipeline
   using 2 excavators."                        Planned Quantity: 12.0 Km
```

### Why Manual Processing Fails Today
1. **Name Mismatch:** Field log says "ROW clearing and grubbing", P6 says `ROW Clearing & Grading`.
2. **Location Mismatch:** Field log says `Chainage 14+200`, P6 tracks `Km 12 to Km 18`.
3. **No Activity Identifier:** The contractor never writes `ACT-1040` on paper field sheets.
4. **Subjective Interpretation:** Planner must manually calculate that 150m equals $0.15\text{ Km}$ and update `ACT-1040` physical percent complete.
