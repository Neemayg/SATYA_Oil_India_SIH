# Institutional Memory & Operational Execution Intelligence

> **Document Type:** Institutional Memory Domain Specification  
> **Governance Status:** Phase 1 Deliverable  
> **Project:** SATYA — Oil India Limited (SIH 2026)  

---

## 1. Executive Summary & Purpose

In current capital project management, when a project finishes, the wealth of operational knowledge—real field execution rates, contractor productivity variations, local weather delay impacts, site terminology aliases, and planner manual corrections—is lost in archived email threads and static spreadsheets.

**Institutional Memory** in SATYA is an operational execution intelligence store. It accumulates verified field performance metrics and human planner feedback over time to continuously refine future schedule baseline estimates and matching accuracy.

---

## 2. Core Components of Institutional Memory

```
+-----------------------------------------------------------------------------------+
|                            INSTITUTIONAL MEMORY STORE                             |
+-----------------------------------------------------------------------------------+
|  1. True Productivity Rates   : Actual production rates per discipline / area     |
|  2. Terminology & Alias Bank  : Synonyms, local jargon, site shorthand dictionary |
|  3. Delay Cause Taxonomy      : Frequency & impact of root-cause delay factors    |
|  4. Planner Correction Log    : Record of human overrides during HITL validation |
|  5. Execution Patterns        : Actual task duration distributions (P10/P50/P90)  |
+-----------------------------------------------------------------------------------+
```

---

## 3. Detailed Component Breakdown

### 3.1 True Field Productivity Rates
* **Description:** Empirical measurement of actual physical output per day across disciplines and site conditions.
* **Examples:**
  * Baseline Plan: $200\text{m}$ trenching per day in Assam clay soil.
  * Verified Actual Rate: $135\text{m}$ trenching per day during monsoon season.
* **Operational Value:** Provides planners with realistic historical productivity factors when drafting future project baselines, preventing overly optimistic initial schedules.
* **Status:** `[REASONABLE DOMAIN ASSUMPTION]`

### 3.2 Terminology & Alias Dictionary Expansion
* **Description:** A growing dictionary mapping informal site jargon to formal WBS activity descriptions.
* **Examples:**
  * Site Jargon: `"HDD 16-inch Pullback"`
  * Formal WBS: `HDD-CW-04: Horizontal Directional Drilling Pipe Pullback`
* **Operational Value:** When a planner manually links an informal phrase to a P6 activity during HITL validation, SATYA saves the alias pair to Institutional Memory, increasing future automated match confidence.
* **Status:** `[CONFIRMED]`

### 3.3 Recurring Delay Cause Taxonomy
* **Description:** Structured catalog of verified bottleneck events explaining schedule variance.
* **Taxonomy Categories:**
  1. *Environmental:* Heavy rainfall, flooding, waterlogging.
  2. *Right-of-Way (ROW):* Land acquisition dispute, forest clearance delay.
  3. *Material:* Pipe delivery delay, valve specification mismatch.
  4. *Quality:* NDT weld failure rework, hydrostatic test burst.
  5. *Equipment:* HDD rig breakdown, excavator fuel shortage.
* **Operational Value:** Quantifies true root causes of delay for executive audit and risk mitigation.
* **Status:** `[REASONABLE DOMAIN ASSUMPTION]`

### 3.4 Planner Correction History & HITL Calibration
* **Description:** Complete log of all human planner overrides during HITL review.
* **Metrics Recorded:**
  * Original AI Match vs. Final Planner Match.
  * Original AI Confidence Score vs. Human Approval Outcome.
  * Reason code selected by planner for override.
* **Operational Value:** Evaluates matching engine accuracy, detects systematic AI false positives, and tunes confidence threshold parameters ($\theta_{\text{review}}$).
* **Status:** `[CONFIRMED]`

### 3.5 Realized Duration Distributions (P10 / P50 / P90)
* **Description:** Statistical distribution of actual task completion times compared to baseline planned durations.
* **Operational Value:** Enables probabilistic schedule risk analysis (PERT/Monte Carlo) grounded in empirical historical execution data rather than theoretical estimates.
* **Status:** `[REASONABLE DOMAIN ASSUMPTION]`

---

## 4. Operational Boundaries: What Institutional Memory Is NOT

To preserve system integrity, Institutional Memory is strictly bounded:
* **NOT Predictive AI Marketing:** It does not promise black-box "magic" project completion prediction.
* **NOT Autonomous Baseline Mutation:** It does not automatically overwrite future schedule baseline estimates without explicit planner approval.
* **NOT Unverified Feedback:** Only *validated* execution events and *approved* planner corrections are ingested into Institutional Memory.
