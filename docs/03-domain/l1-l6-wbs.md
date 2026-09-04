# L1-L6 WBS Breakdown & Operational Matching Dynamics

> **Document Type:** Domain Schedule Structure Specification  
> **Governance Status:** Phase 1 Deliverable  
> **Project:** SATYA — Oil India Limited (SIH 2026)  

---

## 1. The L1 - L6 Schedule Hierarchy Breakdown

In major capital projects undertaken by Oil India Limited, project schedules are organized into a 6-tier Work Breakdown Structure (WBS) hierarchy.

```
L1: Executive Milestone Schedule   (Portfolio / Board Level)
 └── L2: Management Summary        (Facility / Field Level)
      └── L3: Project Control      (Contract Package / Master Level)
           └── L4: Execution Plan  (Discipline / Area Package Level)
                └── L5: Work Package Schedule   <--- [SATYA PRIMARY TARGET]
                     └── L6: Task / Step Breakdown <--- [SATYA SECONDARY TARGET]
```

### Detailed Level Definitions

| WBS Level | Level Name | Typical Granularity | Primary Owner / User | Update Frequency | SATYA Matching Role |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **L1** | Executive Summary | Major Milestones (e.g., "GGS-3 Commissioning") | Oil India Board / CMD | Quarterly | Derived Rollup Target |
| **L2** | Management Summary | Sub-System / Plants (e.g., "Mainline Pipeline 120km") | Executive Director / GM | Monthly | Derived Rollup Target |
| **L3** | Project Control | Contract Packages (e.g., "Civil & Structural Package A") | Project Manager / EPC Lead | Bi-Weekly / Monthly | Rollup & Progress Verification Target |
| **L4** | Execution Plan | Area / Discipline (e.g., "Piping Fabrication Zone 1") | Lead Discipline Engineer | Weekly | WBS Structural Grounding Context |
| **L5** | Work Package | Discrete Deliverable (e.g., `ACT-3020: HDD Crossing River A`) | Planning Engineer / Site Eng. | Daily / Weekly | **PRIMARY MATCHING TARGET** |
| **L6** | Task / Step | Shift Activity (e.g., `STEP-04: Pullback 16" Pipe`) | Field Supervisor / Contractor | Shift / Daily | **SECONDARY / GRANULAR TARGET** |

---

## 2. Why L5 / L6 Are the Operational Matching Targets

* **L1 - L4 Schedules:** Too coarse for field event alignment. Mapping a DPR note like "150m trenching dug" to an L2 activity (`Mainline Pipeline Project`) provides zero actionability.
* **L5 (Work Package Level):** Represents discrete, physically measurable work items with baseline start/finish dates, assigned resources, and quantities (e.g., `Trenching Section 2 - Km 10 to Km 15`). This is the standard Primavera P6 activity level where actual progress percentage and actual start/finish dates must be recorded.
* **L6 (Task/Step Level):** Represents shift-level execution steps. When available in detailed P6 baselines, L6 activities provide direct 1:1 mapping with field log entries.

---

## 3. Parent-Child WBS Relationships & Inheritance

In Primavera P6, every activity inherits contextual attributes from its parent WBS nodes:

```
[WBS Root]: Oil India Upper Assam Field Development
 └── [L2]: GGS-3 (Gas Gathering Station 3)
      └── [L3]: EPC Package 01 - Mechanical & Piping
           └── [L4]: Offsite Piping & Cross-Country
                └── [L5]: ACT-4020: Mainline Pipeline Trenching (Km 10 - 15)
```

* **Structural Fingerprint Inheritance:** `ACT-4020` inherits:
  * Facility Location: `GGS-3 / Upper Assam`
  * Package: `EPC Package 01`
  * Discipline: `Civil / Piping`
  * Predecessor: `ACT-4010 (ROW Clearing Km 10 - 15)`
  * Successor: `ACT-4030 (Pipe Stringing Km 10 - 15)`

---

## 4. Field Observation vs. L5/L6 Activity: Conceptual Discrepancy

A field observation is an empirical record of an execution event; an L5/L6 activity is a scheduled work container. They differ across 4 fundamental axes:

| Axis | Field Observation | L5/L6 Schedule Activity |
| :--- | :--- | :--- |
| **Nature** | Historical empirical fact ("Work happened") | Planned target baseline ("Work scheduled") |
| **Granularity** | Micro-segment (e.g., "12 joints welded today") | Macro-package (e.g., "Weld 450 joints in Zone B") |
| **Identifier** | Descriptive narrative + chainage location | Unique alphanumeric code (e.g., `ACT-3020`) |
| **Boundaries** | Arbitrary shift/crew boundary | Formal WBS deliverable boundary |

---

## 5. Granularity Mismatch Dynamics & Mapping Cardinalities

Granularity mismatch creates ambiguity during automated matching. SATYA models 4 distinct cardinality patterns:

```
1:1 Mapping         [1 Field Obs]  ====================>  [1 L5 Activity]
1:N Mapping         [1 Field Obs]  ======+=============>  [L5 Activity A]
                                         +------------->  [L5 Activity B]
N:1 Mapping         [Field Obs 1]  ------+
                    [Field Obs 2]  ----->+------------->  [1 L5 Activity]
                    [Field Obs 3]  ------+
N:M Mapping         [Field Obs A]  <==== Complex ======>  [L5 Activity 1]
                    [Field Obs B]  <==== Network ======>  [L5 Activity 2]
```

1. **One-to-One ($1:1$):** A specific field report maps cleanly to a single L5 activity (e.g., "Hydrotest for Vessel V-101 completed" $\rightarrow$ `ACT-8010: Hydrotest Vessel V-101`).
2. **One-to-Many ($1:N$):** A single field report covers multiple schedule activities (e.g., "Cleared ROW and completed trenching Km 12-14" $\rightarrow$ Maps to both `ACT-1020 ROW Clearing` and `ACT-1030 Trenching`).
3. **Many-to-One ($N:1$):** Multiple daily field reports contribute incrementally to a single long-duration L5 activity (e.g., 30 daily welding reports mapping to `ACT-2050: Mainline Welding Zone 1`).
4. **Many-to-Many ($N:M$):** Complex multi-crew weekly reports covering multiple geographic sections and WBS packages simultaneously.

---

## 6. Hierarchy Distinction: Conceptual Model vs. Project-Specific Implementation

* **Conceptual Hierarchy:** Standard 6-level WBS structure defined in project controls theory.
* **Project-Specific Implementation:** `[TO BE VALIDATED]` Actual Oil India projects may use varying WBS naming conventions, 4-tier vs. 6-tier P6 layouts, or custom activity ID codes (e.g., `OIL-GGS3-CIV-049`).
* **SATYA Requirement:** The matching engine must remain agnostic to specific WBS string templates, relying instead on structural parent-child trees and Activity Fingerprints.
