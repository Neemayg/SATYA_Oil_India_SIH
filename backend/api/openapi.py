"""
SATYA OpenAPI 3.0 Specification Generator (Phase 11)
Generates full OpenAPI 3.0 schema describing all SATYA REST API routes, schemas, and status codes.
"""

from typing import Dict, Any

def generate_openapi_schema() -> Dict[str, Any]:
    """
    Generates OpenAPI 3.0 JSON specification document.
    """
    return {
        "openapi": "3.0.3",
        "info": {
            "title": "SATYA Application API (Schedule-Aligned Truth & Yield Analytics)",
            "description": "Evidence-backed Execution Truth Layer REST API for Oil India Limited (SIH 2026). Exposes core execution event ingestion, activity fingerprinting, schedule matching, evidence/trust evaluation, HITL planner review queue, and baseline-immutable progress projections.",
            "version": "1.0.0",
            "contact": {
                "name": "SATYA Core Engineering Team",
                "url": "https://github.com/Neemayg/SATYA_Oil_India_SIH"
            }
        },
        "servers": [
            {
                "url": "http://127.0.0.1:8000",
                "description": "Local SATYA Application API Server"
            }
        ],
        "paths": {
            "/api/v1/health": {
                "get": {
                    "summary": "Runtime Operational Health Check",
                    "description": "Returns operational status of API and SQLite database engine.",
                    "responses": {
                        "200": {
                            "description": "Service is operational.",
                            "content": {
                                "application/json": {
                                    "example": {
                                        "status": "healthy",
                                        "service": "satya-api",
                                        "database": "healthy",
                                        "api_version": "v1"
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "/api/v1/openapi.json": {
                "get": {
                    "summary": "OpenAPI Specification",
                    "description": "Returns full OpenAPI 3.0 specification JSON schema.",
                    "responses": {
                        "200": {"description": "OpenAPI specification JSON."}
                    }
                }
            },
            "/api/v1/ingestion/upload": {
                "post": {
                    "summary": "Ingest Document or Raw Text Payload",
                    "description": "Processes raw field text or document payload, creates SourceDocument and ExecutionEvent records preserving 100% provenance.",
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "required": ["project_id", "content"],
                                    "properties": {
                                        "project_id": {"type": "string", "example": "PRJ-NBG-2026"},
                                        "source_type": {"type": "string", "example": "DPR_EXCEL"},
                                        "file_name": {"type": "string", "example": "dpr_reports.txt"},
                                        "content": {"type": "string", "example": "2026-09-02: Mainline trench excavation 350m completed on PL-NBG-SEC1 ACT-1010. QA pending."}
                                    }
                                }
                            }
                        }
                    },
                    "responses": {
                        "201": {"description": "Source ingested successfully."},
                        "400": {"description": "Invalid input payload."},
                        "422": {"description": "Unprocessable payload entity."}
                    }
                }
            },
            "/api/v1/hitl/queue": {
                "get": {
                    "summary": "Query Prioritized Planner Review Queue",
                    "description": "Fetches review queue items ranked deterministically by priority tier (P1 > P2 > P3 > P4) and tie-breaking rules.",
                    "parameters": [
                        {"name": "project_id", "in": "query", "required": False, "schema": {"type": "string"}},
                        {"name": "priority", "in": "query", "required": False, "schema": {"type": "string"}}
                    ],
                    "responses": {
                        "200": {"description": "Review queue list."}
                    }
                }
            },
            "/api/v1/hitl/decisions": {
                "post": {
                    "summary": "Submit Planner Validation Decision",
                    "description": "Submits planner decision (VALIDATE, CHANGE_MATCH, REJECT, REQUEST_EVIDENCE, DEFER). Enforces Decision State Snapshot Lock and returns 409 Conflict if decision is submitted against stale review state.",
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "required": ["event_id", "planner_id", "decision_type", "reviewed_trust_version", "reviewed_match_result_id", "reviewed_evidence_assessment_id"],
                                    "properties": {
                                        "event_id": {"type": "string", "example": "EVT-1010"},
                                        "planner_id": {"type": "string", "example": "PLN-CHIEF-01"},
                                        "decision_type": {"type": "string", "example": "CHANGE_MATCH"},
                                        "reviewed_trust_version": {"type": "integer", "example": 1},
                                        "reviewed_match_result_id": {"type": "string", "example": "MTH-492F01A8"},
                                        "reviewed_evidence_assessment_id": {"type": "string", "example": "EVA-89A120FB"},
                                        "selected_activity_id": {"type": "string", "example": "ACT-1020"},
                                        "override_reason_category": {"type": "string", "example": "SPATIAL_CHAINAGE_RECURRENCE"},
                                        "reason_notes": {"type": "string", "example": "Re-mapped based on chainage survey."}
                                    }
                                }
                            }
                        }
                    },
                    "responses": {
                        "200": {"description": "Decision accepted and versioned TrustAssessment generated."},
                        "400": {"description": "Invalid decision payload or Activity ID."},
                        "404": {"description": "Target event not found."},
                        "409": {"description": "STALE_REVIEW_STATE: Decision submitted against superseded trust version or match result ID."}
                    }
                }
            },
            "/api/v1/projections/generate": {
                "post": {
                    "summary": "Generate Baseline-Immutable Schedule Projection",
                    "description": "Derives activity-level progress, forecast finish dates, and schedule variances from trusted execution events.",
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "required": ["project_id"],
                                    "properties": {
                                        "project_id": {"type": "string", "example": "PRJ-NBG-2026"},
                                        "as_of_date": {"type": "string", "example": "2026-09-05"}
                                    }
                                }
                            }
                        }
                    },
                    "responses": {
                        "200": {"description": "ScheduleProjection snapshot generated."}
                    }
                }
            }
        }
    }
