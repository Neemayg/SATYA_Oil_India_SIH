# MVP Scope Definition & Feature Classification Matrix

> **Document Type:** MVP Scope Specification & Out-of-Scope Guardrails  
> **Governance Status:** Phase 2 Deliverable  
> **Project:** SATYA — Oil India Limited (SIH 2026)  

---

## 1. MVP Scope Core Strategy

The objective of the SATYA Minimum Viable Product (MVP) is to **convincingly solve and demonstrate the core SIH problem statement**: establishing an evidence-backed Execution Truth Layer between heterogeneous field execution observations and Primavera L5/L6 schedule activities.

To ensure deliverability for SIH 2026, the MVP scope is strictly bounded to high-impact core intelligence features, avoiding unnecessary technology inclusions or feature creep.

---

## 2. Feature Scope Classification Matrix

```
                          SATYA FEATURE SCOPE BOUNDARY
+-----------------------------------------------------------------------------------+
| MUST HAVE FOR SIH DEMO (Core MVP Engine & Interface)                             |
|  - Schedule Import (.xer/.xml) & Activity Fingerprinting                         |
|  - Multi-Format Field Report Ingestion (PDF, Excel, Text, Transcript Payload)     |
|  - Execution Event Extraction with Provenance                                     |
|  - Schedule-Aware Matching Engine (MATCHED / AMBIGUOUS / UNMATCHED / CONFLICTED) |
|  - Confidence Scoring ($[0.0, 1.0]$) & Multi-Modal Evidence Linkage               |
|  - Active Conflict Detection & Evidence Gap Flagging                              |
|  - Human-in-the-Loop (HITL) Planner Validation Queue                              |
|  - Trusted Execution Event Creation & Audit-Proof Schedule Projection View        |
|  - Institutional Memory Store (Alias Expansion & Override Tracking)              |
+-----------------------------------------------------------------------------------+
| SHOULD HAVE (Post-MVP Enhancements)                                               |
|  - Multi-Project Portfolio Comparison Dashboard                                  |
|  - Automated PDF/Excel Transmittal Generator                                      |
|  - Advanced PERT / Monte Carlo Duration Variance Curves                           |
+-----------------------------------------------------------------------------------+
| OUT OF SCOPE (Explicitly Excluded Technologies)                                   |
|  - WhatsApp / Telecom Bot Integration       - Drones / Computer Vision          |
|  - Real-Time Voice Assistant ASR            - Digital Twin 3D Rendering         |
|  - Native Mobile App                      - Enterprise ERP / SAP Integration  |
|  - IoT Sensor Streaming Networks            - Blockchain Ledger                 |
+-----------------------------------------------------------------------------------+
```

---

## 3. Detailed Out-of-Scope Feature Evaluation Table

The guiding engineering principle is: **"Do not add technology simply to make the architecture look innovative."**

| Candidate Technology / Feature | Necessary for Core Problem? | Helps SIH Demo? | Scope Classification | Engineering & Operational Rationale |
| :--- | :--- | :--- | :--- | :--- |
| **WhatsApp / Telecom Bot** | No | No | `OUT OF SCOPE` | Unnecessary complexity for MVP. Field reports can be submitted via clean web transmittal forms or file drops. |
| **Real-Time Voice Assistant / ASR** | No | No | `OUT OF SCOPE` | Real-time speech recognition across regional accents adds audio processing overhead without improving core schedule matching math. Voice input can be ingested as text transcript payloads. |
| **Production-Grade Heavy OCR** | No | No | `OUT OF SCOPE` | Handwritten scribble OCR is error-prone. MVP assumes clean PDF text, digital Excel, or form inputs. |
| **Native Mobile App (iOS/Android)** | No | No | `OUT OF SCOPE` | Mobile app development distracts from core matching logic. A responsive web UI is sufficient for all devices. |
| **IoT Sensor Streaming Networks** | No | No | `OUT OF SCOPE` | Construction sites operate on daily shift cycles, not sub-second IoT telemetry. |
| **Drones & Computer Vision** | No | No | `OUT OF SCOPE` | Computer vision video processing is out of scope. Site photos are ingested as geotagged image attachments. |
| **Digital Twin 3D Rendering** | No | No | `OUT OF SCOPE` | 3D BIM rendering is a visual gimmick that does not solve text-to-schedule matching logic. |
| **Predictive Delay AI Forecasting** | No | No | `FUTURE / POST-MVP` | Predictive delay forecasting relies on unproven assumptions. MVP focuses on establishing trusted actual progress first. |
| **Autonomous Schedule Modification** | No | **STRICTLY PROHIBITED** | `OUT OF SCOPE` | Violates Rule 13 & Rule 1. AI must never mutate Primavera baselines autonomously without planner approval. |
| **Enterprise SAP / Primavera API Integration** | No | No | `OUT OF SCOPE` | Requires live enterprise servers. MVP uses file import/export (`.xer`, `.xml`). |
| **Blockchain Distributed Ledger** | No | No | `OUT OF SCOPE` | A standard SQL/PostgreSQL append-only database with cryptographic SHA-256 hashes provides full auditability without blockchain overhead. |
| **Real-Time GPS Asset Tracking** | No | No | `OUT OF SCOPE` | GPS hardware tracking is out of scope. Spatial chainages are extracted from report text. |

---

## 4. MVP Definition of Done (Exit Criteria)

The MVP phase implementation is complete when:
1. System ingests a valid Primavera P6 `.xer` file and extracts 1,000+ L5 activities into Activity Fingerprints.
2. System ingests sample multi-format DPRs, extracts `ExecutionEvent` records, and retains 100% provenance metadata.
3. Matching Engine correctly evaluates events into `MATCHED`, `AMBIGUOUS`, `UNMATCHED`, or `CONFLICTED` statuses.
4. Confidence Scoring and Evidence Linkage correctly auto-pass high-confidence events ($\ge 0.85$) and route low-confidence events to HITL review.
5. Conflict Engine correctly flags simulated contradictory contractor vs. QA claims.
6. HITL interface enables 1-click planner validation, logging human overrides to Institutional Memory.
7. System generates an audit-proof Schedule Projection transmittal showing proposed Primavera updates backed by evidence links.
