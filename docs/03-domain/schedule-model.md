# Schedule Baseline Domain Model & Activity Fingerprinting

> **Document Type:** Schedule Domain Model Specification  
> **Governance Status:** Phase 1 Deliverable  
> **Project:** SATYA — Oil India Limited (SIH 2026)  

---

## 1. Baseline Schedule Domain Model

In SATYA, an ingested project schedule baseline (imported from Primavera P6 `.xer` or MS Project `.xml`) is modeled as a directed acyclic graph (DAG) of activities embedded within a hierarchical WBS tree.

```
+-----------------------------------------------------------------------------------+
|                            BASELINE SCHEDULE MANIFEST                             |
|  - Project Meta: ID, Name, Baseline Date, Calendar Settings                       |
|  - WBS Tree: Nodes, Parent-Child Hierarchy                                        |
|  - Activity Entities: Attributes, Temporal Bounds, Quantities                      |
|  - Dependency Graph: Predecessor & Successor Logic Ties                           |
+-----------------------------------------------------------------------------------+
```

---

## 2. Activity Entity Attribute Breakdown

Every candidate L5/L6 activity in the baseline manifest possesses 4 key attribute groups:

### 2.1 Identity & Semantic Attributes
* `activity_id`: Unique string identifier in schedule (e.g., `ACT-3490`). `[CONFIRMED]`
* `activity_name`: Text description (e.g., `Mainline Pipeline Welding - Sec B`). `[CONFIRMED]`
* `wbs_id`: Foreign key to parent WBS node. `[CONFIRMED]`
* `wbs_path`: Full hierarchical string path (e.g., `OIL.GGS3.CIV.MAINLINE`). `[CONFIRMED]`
* `discipline`: Engineering discipline code (e.g., `CIVIL`, `PIPING`, `E&I`). `[CONFIRMED]`

### 2.2 Temporal & Constraint Attributes
* `planned_start`: Early planned start timestamp. `[CONFIRMED]`
* `planned_finish`: Early planned finish timestamp. `[CONFIRMED]`
* `late_start`: Late start bound calculated by Critical Path Method (CPM). `[REASONABLE DOMAIN ASSUMPTION]`
* `late_finish`: Late finish bound calculated by CPM. `[REASONABLE DOMAIN ASSUMPTION]`
* `baseline_duration`: Total planned duration (days/hours). `[CONFIRMED]`
* `total_float`: Schedule float/slack available before critical path impact. `[REASONABLE DOMAIN ASSUMPTION]`

### 2.3 Spatial & Physical Attributes
* `location_tag`: Facility, field, site zone, or well-pad designation. `[REASONABLE DOMAIN ASSUMPTION]`
* `start_chainage`: Geographical start point for linear projects (e.g., `Km 12.000`). `[REASONABLE DOMAIN ASSUMPTION]`
* `end_chainage`: Geographical end point for linear projects (e.g., `Km 18.500`). `[REASONABLE DOMAIN ASSUMPTION]`
* `planned_quantity`: Scalar target quantity (e.g., `6500.0`). `[CONFIRMED]`
* `unit_of_measure`: Measurement unit (e.g., `Meters`, `Joints`, `MT`, `Cu.M`). `[CONFIRMED]`

### 2.4 Logical Dependency Attributes
* `predecessors`: Array of activity IDs that must precede this activity (with tie types: `FS`, `SS`, `FF`, `SF` and lag). `[CONFIRMED]`
* `successors`: Array of activity IDs that follow this activity. `[CONFIRMED]`

---

## 3. Conceptual Derivation of the Activity Fingerprint

An **Activity Fingerprint** is a multi-dimensional context signature generated for each baseline activity to enable fuzzy, semantic, and structural matching against unstructured field observations.

```
                           +----------------------------------+
                           |     SEMANTIC VECTOR SUB-SPACE    |
                           |  (Name, Description, Keywords,   |
                           |   Discipline Aliases, UOM)       |
                           +----------------------------------+
                                            |
                                            v
+-----------------------------------+   +-----------------------------------+
|    STRUCTURAL WBS SUB-SPACE       |   |      ACTIVITY FINGERPRINT         |
| (WBS Path, Predecessors,          |-->|                                   |
|  Successors, Parent Package)      |   |  Multi-Vector Signature Object    |
+-----------------------------------+   +-----------------------------------+
                                            ^
                                            |
                           +----------------------------------+
                           |    TEMPORAL & SPATIAL SUB-SPACE  |
                           | (Active Time Window, Chainage,   |
                           |  Location Zone, Float Bounds)    |
                           +----------------------------------+
```

### Fingerprint Components
1. **Semantic Signature:** High-dimensional embedding vector representing `activity_name`, `wbs_path`, discipline keywords, and localized aliases from Institutional Memory.
2. **Structural Signature:** Topology encoding of parent WBS nodes and immediate predecessor/successor activities to enforce dependency sanity during matching.
3. **Spatial Signature:** Geographical chainage interval $[S_{\text{chain}}, E_{\text{chain}}]$ or location boundary tag.
4. **Temporal Window:** Active execution interval $[T_{\text{start}} - \Delta t, T_{\text{finish}} + \Delta t]$ defining valid temporal bounds for matching events.

---

## 4. Schedule Constraints, CPM Logic, and Date Interaction

* **Critical Path Method (CPM):** Schedule logic dictates that an activity cannot validly start before its `Finish-to-Start (FS)` predecessors are complete.
* **Date Interaction Rules:**
  * If a field observation indicates an activity started on `2026-09-01`, but its predecessor is reported incomplete, SATYA flags a `LogicConflict` or `Out-of-Sequence Execution` warning.
  * `Actual Start` locks the activity start timestamp; `Actual Finish` locks completion and sets `Remaining Duration = 0`.
