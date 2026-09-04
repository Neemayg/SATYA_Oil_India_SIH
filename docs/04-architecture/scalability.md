# Scalability & Deployment Architecture

> **Document Type:** System Scalability & Growth Specification  
> **Governance Status:** Phase 3 Deliverable  
> **Project:** SATYA — Oil India Limited (SIH 2026)  

---

## 1. Prototype to Enterprise Evolution Roadmap

SATYA is architected to scale seamlessly from a lightweight SIH prototype to an enterprise multi-project deployment for Oil India Limited.

```
SIH 2026 PROTOTYPE                             ENTERPRISE PRODUCTION DEPLOYMENT
(Modular Monolith)                             (Distributed Microservices & Queues)

┌───────────────────────────────┐              ┌──────────────────┐    ┌──────────────────┐
│ SATYA Modular Monolith        │              │ Schedule Service │    │ Extraction Worker│
│  - Single Process             │              └────────┬─────────┘    └────────┬─────────┘
│  - In-Memory Queue            │ ======>               │                       │
│  - Relational Storage         │              ┌────────┴───────────────────────┴─────────┐
│  - Local Cache                │              │  Distributed Event Bus / Message Queue   │
└───────────────────────────────┘              └────────┬───────────────────────┬─────────┘
                                                        │                       │
                                               ┌────────┴─────────┐    ┌────────┴─────────┐
                                               │ Match Engine Svc │    │ Projection Svc   │
                                               └──────────────────┘    └──────────────────┘
```

---

## 2. Scalability Mechanics & Architectural Strategies

1. **Asynchronous Batch Ingestion:** Field DPR uploads and voice transcript processing execute asynchronously via background job queues, preventing API timeouts on large multi-tab Excel files.
2. **Project-Level Data Isolation:** Database schemas and search indexes enforce strict tenant/project isolation (`project_id`), ensuring vector candidate retrieval scans only candidate fingerprints belonging to the active project baseline.
3. **Fingerprint Caching Strategy:** Activity Fingerprints are pre-computed upon schedule import and cached in memory, eliminating redundant embedding generation during daily matching runs.
4. **Idempotent Ingestion Design:** Re-uploading the same DPR file (identical SHA-256 hash) returns the existing ingestion record without duplicating events or matching runs.
