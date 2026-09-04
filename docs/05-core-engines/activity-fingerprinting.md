# Activity Fingerprinting Core Engine Specification

> **Document Type:** Core Engine Implementation Specification  
> **Governance Status:** Phase 6 Implementation Deliverable  
> **Project:** SATYA — Oil India Limited (SIH 2026)  

---

## 1. Engine Overview & Architecture

The **Activity Fingerprinting Engine** (Phase 6) converts high-level Primavera P6 / MS Project L5/L6 baseline schedule activities into rich, searchable, multi-dimensional `ActivityFingerprint` records.

Rather than relying solely on surface-level text matching, Phase 6 constructs a multi-layer searchable identity for every schedule activity combining **Structural**, **Semantic**, **Spatial/Zone**, **Temporal**, and **Terminology Intelligence**.

```
[PRIMAVERA P6 / MS PROJECT BASELINE SCHEDULE]
                     │
                     ▼
  ┌─────────────────────────────────────┐
  │ 1. WBS HIERARCHY TOPOLOGICAL PARSER │ ──> (Builds wbs_name_path e.g. "Project > Mainline > Sec 1")
  └──────────────────┬──────────────────┘
                     │
                     ▼
  ┌─────────────────────────────────────┐
  │ 2. TERMINOLOGY INTELLIGENCE ENGINE  │ ──> (Expands ROW -> Right of Way, HDD -> River Crossing, NDT, etc.)
  └──────────────────┬──────────────────┘
                     │
                     ▼
  ┌─────────────────────────────────────┐
  │ 3. SEMANTIC ENTITY & ACTION PARSER  │ ──> (Extracts action_verbs, entity_nouns, synonyms, search_tokens)
  └──────────────────┬──────────────────┘
                     │
                     ▼
  ┌─────────────────────────────────────┐
  │ 4. ACTIVITY FINGERPRINT GENERATOR   │ ──> (Constructs immutable ActivityFingerprint object)
  └──────────────────┬──────────────────┘
                     │
                     ▼
  ┌─────────────────────────────────────┐
  │ 5. SQLITE FINGERPRINT REPOSITORY    │ ──> (Indexed activity_fingerprints table)
  └─────────────────────────────────────┘
```

---

## 2. Multi-Dimensional Fingerprint Schema

| Feature Layer | Fingerprint Attribute | Description |
| :--- | :--- | :--- |
| **Identity** | `fingerprint_id`, `activity_id`, `project_id` | Immutable primary key & baseline Activity ID (`ACT-1010`) |
| **Structural Context** | `wbs_id`, `wbs_code`, `wbs_name_path` | Topological hierarchy path (e.g. `North Basin Gas Expansion > Cross-Country Mainline Pipeline > Pipeline Section 1`) |
| **Network Context** | `predecessors`, `successors`, `is_critical` | Primavera P6 CPM logic links and critical path flag |
| **Discipline & Zone** | `discipline`, `area_location`, `equipment_tag`, `line_number`, `start_km`, `end_km` | Physical zone, chainage range (e.g. `Km 0.0 to 2.0`), equipment/line tags |
| **Temporal Window** | `planned_start`, `planned_finish`, `baseline_duration_days` | Primavera baseline schedule window |
| **Yield & Quantity** | `planned_quantity`, `unit_of_measure` | Physical baseline targets (e.g. `2000.0 Meters`) |
| **Terminology Intelligence** | `action_verbs`, `entity_nouns`, `synonyms`, `field_aliases` | Domain lexicon expansions (e.g., `ROW` $\leftrightarrow$ `Right of Way`, `clearing` $\leftrightarrow$ `grading`/`row prep`) |
| **Search Index** | `search_tokens` | Normalized bag-of-words token set for candidate generation |

---

## 3. Implemented Backend Modules

* [`backend/models/domain_models.py`](file:///Users/neemaysmac/Desktop/OIL_India_SIH/backend/models/domain_models.py): Defines `ActivityFingerprint` dataclass.
* [`backend/fingerprinting/terminology_engine.py`](file:///Users/neemaysmac/Desktop/OIL_India_SIH/backend/fingerprinting/terminology_engine.py): Lexicon engine providing Oil & Gas EPC abbreviation expansion (`ROW`, `HDD`, `GGS`, `NDT`, `DCS`, `TPIA`), action verb extraction, and field alias generation.
* [`backend/fingerprinting/fingerprint_generator.py`](file:///Users/neemaysmac/Desktop/OIL_India_SIH/backend/fingerprinting/fingerprint_generator.py): WBS hierarchy topological parser and multi-dimensional fingerprint generator.
* [`backend/persistence/database_engine.py`](file:///Users/neemaysmac/Desktop/OIL_India_SIH/backend/persistence/database_engine.py): SQLite persistence engine with indexed `activity_fingerprints` table.
* [`backend/services/fingerprint_service.py`](file:///Users/neemaysmac/Desktop/OIL_India_SIH/backend/services/fingerprint_service.py): Service orchestrator indexing 100% of synthetic baseline schedule activities.

---

## 4. Verification & Baseline Indexing Coverage

* **Synthetic Project 1 (`PRJ-NBG-2026`):** 60 / 60 Activities fingerprinted (100%).
* **Synthetic Project 2 (`PRJ-SCP-2026`):** 41 / 41 Activities fingerprinted (100%).
* **Total Indexed Schedule Vocabulary:** 101 Activity Fingerprints cached and queryable.

---

## 5. Architectural Scoping Safeguard

Phase 6 strictly satisfies scope boundaries:
1. **No Schedule Matching:** Fingerprints provide identity indexing only; matching is strictly deferred to Phase 7.
2. **No Data Mutation:** Raw baseline schedule files are preserved unchanged.
3. **No Heavy Infrastructure:** Built with 100% standard Python library and local SQLite.
