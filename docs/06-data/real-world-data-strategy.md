# Real-World Data Reconnaissance & Strategy Report

> **Document Type:** Real-World Data Reconnaissance & Benchmark Strategy  
> **Governance Status:** Phase 4.5 Deliverable  
> **Project:** SATYA — Oil India Limited (SIH 2026)  

---

## 1. Objective & Non-Training Data Principle

The primary objective of Phase 4.5 is to conduct a targeted reconnaissance of publicly accessible real-world project execution and progress reporting data to answer the core question:

> *"Does SATYA's synthetic world resemble physical project execution reality closely enough?"*

### Critical Architectural Distinction
In SATYA, data categories are strictly separated by operational role:
* **Synthetic Dataset (`data/synthetic/`):** Controlled, fully-annotated benchmark dataset designed to test specific domain scenarios (`SCN-001` to `SCN-015`).
* **Real-World Reconnaissance Data:** Unlabeled or reference material used for robustness evaluation and language pattern discovery. **It is NOT "training data"** for machine learning models. SATYA does not silently learn from arbitrary unvalidated real-world documents.
* **Institutional Memory Store:** Accumulated historical execution intelligence derived exclusively from *validated* human planner sign-offs and approved project actuals.

---

## 2. Real-World Human Execution Language Patterns

Analysis of real-world construction progress reports, site diaries, and EPC transmittals reveals complex human reporting language patterns that differ significantly from simple textbook statements:

```
CLEAN SYNTHETIC TEXT:
"24-inch line erection commenced at Unit 3."

REAL-WORLD HUMAN REPORTING TEXT:
"U3 24" line spool-5 erection taken up in night shift, balance 2 joints pending; clearance awaited from QA."
```

### Key Real-World Reporting Patterns Identified

| Pattern Category | Real-World Reporting Examples | Operational Challenges Posed |
| :--- | :--- | :--- |
| **Heavy Abbreviation & Shorthand** | `"U3 24in sp-5 erect taken up; bal 2 jts pend"` | Keyword search and standard regex parsers fail; requires domain expansion dictionaries. |
| **Mixed & Dual Units** | `"Erected 3 spools (18 meters, 48 dia-inch welding completed)"` | Multiple quantity metrics in a single line; parser must extract correct UOM matching schedule baseline. |
| **Shift & Temporal Context** | `"Night shift 02-Sep taken up; 2nd shift today halted due to rain"` | Relative temporal phrases requiring resolution against report transmittal metadata. |
| **QA Dependency & Hold Points** | `"Clearance awaited from QA; NDT radiography clearance pending"` | Progress physically achieved on site, but locked behind quality hold point. |
| **Partial Completion & Remaining Work** | `"Trenching done up to Ch 14+200, balance 150m stuck in hard rock"` | Scalar progress reported along with explicitly stated remaining scope. |
| **Multi-Entity Compound Sentences** | `"Laid 150m 16" pipe, completed 4 root passes, and backfilled 80m near stream"` | Single sentence containing 3 distinct work actions across 3 schedule activities. |
| **Work Front & Crew Identification** | `"Gang 2 operating at Front B near well-pad 14"` | Micro-location and crew assignment tags requiring spatial mapping. |

---

## 3. Synthetic Dataset Gap Analysis

Comparing real-world language patterns against `data/synthetic/` reveals key areas of strength and specific gaps:

```
SYNTHETIC DATASET COVERAGE GAP MATRIX
┌───────────────────────────────────────────────────────────────────────────────────┐
│ WELL-REPRESENTED IN SYNTHETIC DATA:                                                │
│  ✔ Explicit Activity ID matching (SCN-001)                                        │
│  ✔ Chainage-based spatial matching (SCN-002)                                      │
│  ✔ Terminology jargon & localized aliases (SCN-003)                               │
│  ✔ Basic acronyms & shorthand (SCN-004)                                           │
│  ✔ Contradictory reports (Contractor vs. QA NDT failure) (SCN-007)                │
│  ✔ Duplicate transmittal detection (SCN-008)                                      │
│  ✔ Out-of-sequence execution warnings (SCN-014)                                  │
├───────────────────────────────────────────────────────────────────────────────────┤
│ UNDERREPRESENTED / PROPOSED FOR FUTURE ENHANCEMENT:                               │
│  ⚠️ Compound sentences containing multiple work actions & remaining quantities    │
│  ⚠️ Specific shift context tags ("Night shift", "Shift 2")                        │
│  ⚠️ Explicit QA Hold Point flags ("Clearance awaited from TPIA")                  │
│  ⚠️ Dual quantity metrics (Dia-Inch vs. Spools vs. Meters)                        │
└───────────────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Proposed Domain & Schema Extensions (Phase 6/7 Reference)

Based on real-world data reconnaissance, the following conceptual extensions are proposed for future extraction pipelines (`PROPOSED DOMAIN EXTENSIONS`):

1. **`shift_context`**: Field to capture shift markers (`DAY_SHIFT`, `NIGHT_SHIFT`, `SHIFT_2`).
2. **`pending_qa_clearance`**: Boolean flag indicating work completed but physically locked awaiting NDT/TPIA sign-off.
3. **`remaining_quantity`**: Field to capture explicit remaining scope stated in text (e.g., `"balance 150m pending"`).
4. **`work_front_tag`**: Informal site front tag (e.g., `"Front B"`, `"Well-Pad 14 Spool Yard"`).

*Note: These extensions are documented conceptually for Phase 5/6 and do not mutate existing Phase 3 JSON schemas.*

---

## 5. Real-World Benchmark Strategy

SATYA establishes a 3-tier strategy for utilizing real-world data:

```
                          REAL-WORLD BENCHMARK STRATEGY
┌───────────────────────────────────────────────────────────────────────────────────┐
│ TIER 1: UNLABELED ROBUSTNESS TESTING                                              │
│  - Ingest public PDF/Excel construction logs (e.g., USACE RMS public logs).      │
│  - Evaluates extraction parser resilience against messy formatting & OCR noise.   │
├───────────────────────────────────────────────────────────────────────────────────┤
│ TIER 2: MANUALLY LABELED GOLD SUBSET                                              │
│  - Small 25-record annotated subset of real-world text snippets.                  │
│  - Used during Phase 15 evaluation to calculate real-world precision & recall.  │
├───────────────────────────────────────────────────────────────────────────────────┤
│ TIER 3: REFERENCE-ONLY DOMAIN DICTIONARY                                          │
│  - Public reports (MoSPI, FIDIC templates) used to seed domain vocabulary aliases.│
│  - Zero raw text stored in repository to respect intellectual property rights.    │
└───────────────────────────────────────────────────────────────────────────────────┘
```

---

## 6. Critical Research Review & Questions Answered

1. **Did we find genuinely useful real-world benchmark data?**  
   *Yes.* Public infrastructure reports (MoSPI PAIMANA, USACE RMS QC logs, academic construction NLP corpora) provide valuable real-world reporting language structures.
2. **Does public real-world data contain direct schedule-to-execution relationships?**  
   *Rarely.* Public government reports provide macro status (L1/L2), while site logs provide micro text. The direct link to Primavera L5/L6 Activity IDs is almost universally absent in public reports—confirming SATYA's core premise!
3. **Can public real-world data provide gold ground truth automatically?**  
   *No.* Public documents do not come with pre-annotated Activity IDs or match outcome labels. Ground truth must be established via small, manually labeled gold evaluation subsets.
4. **What aspects of our synthetic dataset appear representative?**  
   Our synthetic dataset's chainage logic, discipline structures, contradiction scenarios (`SCN-007`), and multi-project baselines (`PRJ-NBG-2026` & `PRJ-SCP-2026`) accurately mirror physical project execution challenges.
5. **Does our current system architecture still appear appropriate?**  
   *Yes.* The 7-stage hybrid matching pipeline, Closed-Vocabulary Guardrail (Rule 5), and threshold-gated HITL validation boundary are fully validated by real-world reporting complexities.
