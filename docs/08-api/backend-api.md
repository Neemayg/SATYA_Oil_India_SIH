# SATYA — Backend Application Services & REST API Specification
**Document Reference:** `docs/08-api/backend-api.md`  
**Active Phase:** Phase 11 — Backend Application Services (🟢 APPROVED & CLOSED)

---

## 1. Executive Summary

Phase 11 establishes a clean, zero-dependency REST API application transport layer over SATYA's core intelligence engines (Phases 5–10).

```
Client (Phase 12 Frontend / External Systems)
  ↓
HTTP API Transport Layer (Phase 11)
  ├── Routing & Query Parameter Resolution
  ├── Request Payload Validation
  ├── Transport Serialization (Thin Layer)
  ├── SATYAError Mapping (HTTP Status Codes)
  └── Configurable CORS Middleware (`SATYA_ALLOWED_ORIGINS`)
  ↓
Existing Application Services
  ├── PipelineService (Phase 5/5.1)
  ├── FingerprintService (Phase 6)
  ├── MatchingService (Phase 7/7.1)
  ├── TrustEvaluatorService (Phase 8)
  ├── ValidationService & PlannerQueueManager (Phase 9)
  └── ScheduleProjectionService (Phase 10)
  ↓
Immutable Ledger & SQLite Database Engine
```

---

## 2. Architectural Design Directives & Constraints

1. **Thin Transport Boundary:** Route handlers delegate business logic entirely to existing application services. Serializers (`backend/api/serializers.py`) format internal domain models into JSON transport payloads without duplicating business rules.
2. **Read-Only Ledger Integrity:** No generic mutation endpoints (`PUT/DELETE /events`, `PUT/DELETE /sources`) exist. Execution events and evidence claims remain immutable append-only records.
3. **HITL REST Snapshot Locking (409 Conflict):** When submitting a human validation decision (`POST /api/v1/hitl/decisions`), the request must specify `reviewed_trust_version`. If the event's trust assessment has been superseded since the planner opened the record, the API rejects the decision with `HTTP 409 Conflict` and error code `STALE_REVIEW_STATE`.
4. **Standardized SATYAError Response Contract:** All error responses return a uniform JSON schema:
   ```json
   {
     "error": {
       "code": "STALE_REVIEW_STATE",
       "message": "Reviewed trust version (v1) is stale. Latest trust version is v2.",
       "details": {"event_id": "EVT-1001", "latest_version": 2},
       "request_id": "REQ-7F9A1B2C",
       "timestamp": "2026-09-04T15:50:00Z"
     }
   }
   ```
5. **Operational Health Endpoint:** `/api/v1/health` provides real-time system, database, and service status without running test suite assertions.
6. **OpenAPI 3.0 Contract:** Schema is programmatically generated and served at `GET /api/v1/openapi.json`.

---

## 3. Complete Endpoint Specification

| Group | Method | Path | Description |
|---|---|---|---|
| **System** | `GET` | `/api/v1/health` | Operational health & service status |
| **System** | `GET` | `/api/v1/openapi.json` | OpenAPI 3.0 Specification |
| **Ingestion** | `POST` | `/api/v1/ingestion/upload` | Ingest raw text/document payload & extract events |
| **Ingestion** | `GET` | `/api/v1/ingestion/sources/{id}` | Bounded source metadata & extracted event IDs |
| **Ingestion** | `GET` | `/api/v1/ingestion/events/{id}` | Detailed execution event & provenance |
| **Fingerprints** | `POST` | `/api/v1/fingerprints/index` | Process & index baseline schedule JSON |
| **Fingerprints** | `GET` | `/api/v1/fingerprints/projects/{id}` | List activity fingerprints for project |
| **Fingerprints** | `GET` | `/api/v1/fingerprints/search` | Search fingerprints (semantic & filters) |
| **Matching** | `POST` | `/api/v1/matching/match` | Perform candidate matching for event |
| **Matching** | `GET` | `/api/v1/matching/events/{id}` | Retrieve match results & candidate scores for event |
| **Evidence & Trust** | `POST` | `/api/v1/evidence/evaluate` | Run evidence claim extraction & trust evaluation |
| **Evidence & Trust** | `GET` | `/api/v1/evidence/events/{id}/trust` | Retrieve versioned trust assessment history |
| **Evidence & Trust** | `GET` | `/api/v1/evidence/events/{id}/conflicts` | Retrieve active conflict flags for event |
| **HITL** | `GET` | `/api/v1/hitl/queue` | Fetch prioritized planner review queue |
| **HITL** | `POST` | `/api/v1/hitl/decisions` | Submit human validation decision with snapshot lock |
| **Projections** | `POST` | `/api/v1/projections/generate` | Calculate progress & generate schedule projection |
| **Projections** | `GET` | `/api/v1/projections/projects/{id}/latest` | Fetch latest schedule projection for project |
| **Projections** | `GET` | `/api/v1/projections/projects/{id}/activities/{act_id}` | Fetch detailed activity progress |

---

## 4. Verification & Testing

The REST API implementation has been verified with 81 automated tests (68 unit tests, 13 integration tests):
- `tests/unit/test_api_endpoints.py`: Verifies endpoint routing, serialization, and status code contracts.
- `tests/unit/test_api_hitl_concurrency.py`: Verifies `409 Conflict` on stale `reviewed_trust_version`.
- `tests/integration/test_api_integration.py`: Verifies complete end-to-end flow from REST ingestion to projection generation.
