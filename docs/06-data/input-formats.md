# Input Formats & Schedule Import Boundary Specifications

> **Document Type:** Input Format & Boundary Specifications  
> **Governance Status:** Phase 3 Deliverable  
> **Project:** SATYA — Oil India Limited (SIH 2026)  

---

## 1. Schedule Import Boundary & Feasibility Analysis

To prevent Primavera P6 format parsing complexity (`.xer` file parsing) from becoming an engineering bottleneck during SIH development, SATYA defines a **Normalized Schedule Import Boundary**.

```
INPUT FORMATS                                NORMALIZED SCHEDULE MANIFEST
┌─────────────────────────────────┐          ┌───────────────────────────────────┐
│ Primavera P6 (.xer)             │          │ Minimum Required Fields:          │
├─────────────────────────────────┤          │ - activity_id     (String)        │
│ Primavera P6 (.xml)             │ ====>    │ - activity_name   (String)        │
├─────────────────────────────────┤          │ - wbs_path        (String)        │
│ MS Project XML (.xml)           │          │ - planned_start   (Timestamp)     │
├─────────────────────────────────┤          │ - planned_finish  (Timestamp)     │
│ Standardized CSV / Excel Import │          │ - planned_qty     (Scalar, Opt)   │
└─────────────────────────────────┘          └───────────────────────────────────┘
```

### Minimum Required Fields vs. Optional Fields

| Field Name | Category | Status | Action if Missing |
| :--- | :--- | :--- | :--- |
| `activity_id` | Identity | **MANDATORY** | Row REJECTED & logged in Import Exception Log. |
| `activity_name` | Identity | **MANDATORY** | Row REJECTED & logged in Import Exception Log. |
| `wbs_path` / `wbs_id` | Hierarchy | **MANDATORY** | Assigned default root WBS node (`WBS.ROOT`). |
| `planned_start` | Temporal | **MANDATORY** | Inferred from parent WBS or project start date. |
| `planned_finish` | Temporal | **MANDATORY** | Calculated from `planned_start` + duration. |
| `discipline` | Attribute | **OPTIONAL** | Inferred via keyword extraction on activity name. |
| `planned_quantity` | Quantity | **OPTIONAL** | Set to default `1.0` (Unit: `Lot` / `Activity`). |
| `predecessors` | Logic | **OPTIONAL** | Treated as independent activity without logic ties. |

---

## 2. Field Observation Source Formats

| Source Type | Accepted File Formats | Machine-Resolvable Provenance Locator | Extraction Method |
| :--- | :--- | :--- | :--- |
| **Excel Daily Report** | `.xlsx`, `.xls`, `.csv` | Sheet name + Cell Reference (`Sheet2!C14`) | Tabular row parser. |
| **PDF Daily Report** | `.pdf` | Page number + Bounding Box (`Page 3, Line 12`) | Text PDF block extractor. |
| **Digital Text Note** | `.txt`, `JSON Payload` | Character / Word Offset (`Chars 140-280`) | Text entity parser. |
| **Voice Transcript** | `JSON Payload` | Audio Timestamp Interval (`01:14 - 01:45`) | Transcript text parser. |
| **Site Image Evidence** | `.jpg`, `.png` | Image SHA-256 + Geotag Metadata | Image metadata reader. |
