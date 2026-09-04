# Structural JSON Schemas & Enumerated State Specifications

> **Document Type:** Structural Schema & Taxonomy Specification  
> **Governance Status:** Phase 3 Deliverable  
> **Project:** SATYA — Oil India Limited (SIH 2026)  

---

## 1. System State & Outcome Enumerations

### 1.1 Event Lifecycle States
```json
{
  "enum_name": "ExecutionEventState",
  "allowed_values": [
    "OBSERVED",
    "EXTRACTED",
    "MATCHED",
    "VALIDATED",
    "PROJECTED_TO_SCHEDULE"
  ]
}
```

### 1.2 Matching Engine Outcomes
```json
{
  "enum_name": "MatchingOutcome",
  "allowed_values": [
    "MATCHED",
    "AMBIGUOUS",
    "UNMATCHED",
    "CONFLICTED"
  ]
}
```

---

## 2. Core Structural JSON Schemas

### 2.1 ExecutionEvent JSON Schema Structure
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "ExecutionEvent",
  "type": "object",
  "required": [
    "event_id",
    "source_id",
    "observed_timestamp",
    "work_action",
    "observed_quantity",
    "unit_of_measure",
    "state",
    "provenance"
  ],
  "properties": {
    "event_id": { "type": "string", "example": "EVT-90412" },
    "source_id": { "type": "string", "example": "SRC-1004" },
    "observed_timestamp": { "type": "string", "format": "date-time" },
    "work_action": { "type": "string", "example": "TRENCHING" },
    "observed_quantity": { "type": "number", "example": 180.0 },
    "unit_of_measure": { "type": "string", "example": "Meters" },
    "discipline": { "type": "string", "example": "CIVIL" },
    "location_tag": { "type": "string", "example": "Km 14.100 - 14.280" },
    "state": { "$ref": "#/definitions/ExecutionEventState" },
    "provenance": {
      "type": "object",
      "required": ["source_type", "locator_type", "locator_value"],
      "properties": {
        "source_type": { "type": "string", "example": "DPR_EXCEL" },
        "locator_type": { "type": "string", "example": "EXCEL_CELL" },
        "locator_value": { "type": "string", "example": "Sheet2!B42" },
        "raw_text_snippet": { "type": "string", "example": "Completed 180m trenching at Ch 14+100" }
      }
    }
  }
}
```

### 2.2 ConfidenceAssessment JSON Schema Structure
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "ConfidenceAssessment",
  "type": "object",
  "required": [
    "assessment_id",
    "event_id",
    "candidate_activity_id",
    "overall_confidence",
    "factor_breakdown"
  ],
  "properties": {
    "assessment_id": { "type": "string" },
    "event_id": { "type": "string" },
    "candidate_activity_id": { "type": "string" },
    "overall_confidence": { "type": "number", "minimum": 0.0, "maximum": 1.0 },
    "factor_breakdown": {
      "type": "object",
      "properties": {
        "semantic_score": { "type": "number" },
        "spatial_score": { "type": "number" },
        "temporal_score": { "type": "number" },
        "discipline_score": { "type": "number" }
      }
    },
    "reasoning_trace": {
      "type": "array",
      "items": { "type": "string" }
    }
  }
}

### 2.3 ActivityFingerprint JSON Schema Structure
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "ActivityFingerprint",
  "type": "object",
  "required": [
    "fingerprint_id",
    "activity_id",
    "wbs_path_string",
    "semantic_embedding_vector",
    "temporal_window_bounds"
  ],
  "properties": {
    "fingerprint_id": { "type": "string", "example": "FPR-1042" },
    "activity_id": { "type": "string", "example": "ACT-3020" },
    "wbs_path_string": { "type": "string", "example": "NORTH_BASIN.GGS3.CIVIL.MAINLINE" },
    "semantic_embedding_vector": { "type": "array", "items": { "type": "number" } },
    "spatial_chainage_interval": {
      "type": "object",
      "properties": {
        "start_km": { "type": "number" },
        "end_km": { "type": "number" }
      }
    },
    "temporal_window_bounds": {
      "type": "object",
      "properties": {
        "planned_start": { "type": "string", "format": "date-time" },
        "planned_finish": { "type": "string", "format": "date-time" }
      }
    }
  }
}
```

### 2.4 CandidateMatch JSON Schema Structure
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "CandidateMatch",
  "type": "object",
  "required": [
    "match_id",
    "event_id",
    "candidate_activity_id",
    "raw_confidence_score",
    "match_status"
  ],
  "properties": {
    "match_id": { "type": "string", "example": "MCH-8801" },
    "event_id": { "type": "string", "example": "EVT-90412" },
    "candidate_activity_id": { "type": "string", "example": "ACT-3020" },
    "raw_confidence_score": { "type": "number", "minimum": 0.0, "maximum": 1.0 },
    "match_status": { "$ref": "#/definitions/MatchingOutcome" }
  }
}
```

### 2.5 Conflict JSON Schema Structure
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Conflict",
  "type": "object",
  "required": [
    "conflict_id",
    "event_id_a",
    "conflict_type",
    "status"
  ],
  "properties": {
    "conflict_id": { "type": "string", "example": "CNF-3012" },
    "event_id_a": { "type": "string", "example": "EVT-90412" },
    "event_id_b": { "type": "string", "example": "EVT-90415" },
    "conflict_type": { "type": "string", "example": "QA_CONTRADICTION" },
    "status": { "type": "string", "example": "UNRESOLVED" }
  }
}
```

### 2.6 InstitutionalMemoryEntry JSON Schema Structure
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "InstitutionalMemoryEntry",
  "type": "object",
  "required": [
    "entry_id",
    "entry_type",
    "jargon_term",
    "formal_activity_name"
  ],
  "properties": {
    "entry_id": { "type": "string", "example": "MEM-0042" },
    "entry_type": { "type": "string", "example": "TERMINOLOGY_ALIAS" },
    "jargon_term": { "type": "string", "example": "HDD 16-inch Pullback" },
    "formal_activity_name": { "type": "string", "example": "HDD-CW-04: Horizontal Directional Drilling Pipe Pullback" },
    "frequency_count": { "type": "integer", "example": 14 }
  }
}
```

```
