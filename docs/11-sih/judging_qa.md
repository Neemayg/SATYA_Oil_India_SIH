# SATYA SIH 2026 Jury & Technical Q&A Guide

**Repository:** SATYA (Schedule-Aligned Truth & Yield Analytics) — Oil India Limited (SIH 2026)  
**Document Path:** `docs/11-sih/judging_qa.md`  
**Purpose:** Prepares the team to answer 13 critical technical, architectural, and business questions during the SIH 2026 jury evaluation Q&A session.

---

## 1. Core Technical & Architectural Questions

### Q1: "Why not just use an LLM like GPT-4 or Gemini to read DPRs and update Primavera directly?"
- **Short Answer**: *LLMs are non-deterministic text generators. They hallucinate non-existent activity IDs, cannot enforce closed schedule boundaries, and lack an immutable audit trail.*
- **Detailed Explanation**:
  > *"Using a pure LLM to update Primavera P6 is dangerous for enterprise infrastructure projects. LLMs generate plausibly-sounding text, but they frequently hallucinate activity IDs (`ACT-9999`) that do not exist in the Primavera schedule. Furthermore, LLMs cannot provide mathematical factor breakdowns ($S_{\text{loc}}, S_{\text{term}}, S_{\text{time}}$) or enforce append-only audit ledgers.*  
  >  
  > *SATYA uses a hybrid architecture: LLMs or NLP models are strictly restricted to Layer 1 event parsing. Scoring, fingerprinting, evidence trust verification, and schedule projection logic are 100% deterministic Python engines with strict closed-vocabulary guardrails."*

---

### Q2: "How is SATYA different from Primavera P6 or MS Project?"
- **Short Answer**: *Primavera P6 is a scheduling and baseline management tool; SATYA is an execution truth layer that reconciles messy field observations INTO Primavera P6.*
- **Detailed Explanation**:
  > *"Primavera P6 requires clean, structured input data (Activity ID, % Complete, Actual Start). Primavera does not know how to read a messy PDF, an Excel DPR snippet, or a site photo saying 'HDD Section 3 crossing completed'. SATYA sits BETWEEN unstructured field observations and Primavera P6, extracting facts, calculating evidence trust, and presenting validated actuals for schedule updating while keeping baseline schedules read-only."*

---

### Q3: "How is SATYA different from a DPR chatbot or document OCR scanner?"
- **Short Answer**: *OCR scanners and chatbots stop at text extraction ("We extracted 420m"). SATYA asks: "Can the schedule safely believe it?"*
- **Detailed Explanation**:
  > *"OCR tools digitize paper into text. Chatbots summarize text. Neither tool understands Primavera WBS structures, predecessor logic, UOM compatibility, or multi-factor confidence scoring. SATYA decomposes text into execution events, fingerprints them against schedule topology, detects evidence conflicts, and enforces human-in-the-loop validation."*

---

### Q4: "How do you prevent hallucinated Activity IDs (Rule 5 Safety)?"
- **Short Answer**: *Through Rule 5 Schedule-Aware Closed Vocabulary Safety enforced at the database and service pipeline layer.*
- **Detailed Explanation**:
  > *"SATYA maintains a closed vocabulary of valid activity IDs extracted from the baseline schedule file (`baseline_schedule.json`). If a field report or an AI model references an explicit ID like `ACT-9999-HALLUCINATED`, our validation engine immediately intercepts it, clears the explicit ID to `None`, and routes the event to un-matched reconciliation. Unrecognized activity IDs can NEVER enter the database or update a schedule."*

---

### Q5: "How does confidence scoring work?"
- **Short Answer**: *Confidence is a multi-factor normalized score $C \in [0.0, 1.0]$ combining identifier, spatial location, technical terminology, WBS context, discipline, and temporal alignment.*
- **Detailed Explanation**:
  > *"Confidence is not a black-box LLM guess. It is calculated deterministically:
  > $$C_{\text{match}} = \text{clamp}(w_{\text{id}} S_{\text{id}} + w_{\text{loc}} S_{\text{loc}} + w_{\text{term}} S_{\text{term}} + w_{\text{wbs}} S_{\text{wbs}} + w_{\text{disc}} S_{\text{disc}} + w_{\text{time}} S_{\text{time}} + S_{\text{alias}}, 0.0, 1.0)$$
  > Each factor is transparently exposed on the Reconciliation Desk UI."*

---

### Q6: "What happens when confidence is low?"
- **Short Answer**: *The event is designated `INSUFFICIENT_EVIDENCE` and conservatively delegated to the Reconciliation Desk for human planner validation.*
- **Detailed Explanation**:
  > *"If $C_{\text{match}} < \theta_{\text{match}} (0.80)$, SATYA refuses to auto-match. It preserves the raw event in an append-only ledger and alerts the planner on the Reconciliation Desk. SATYA prioritizes safety over false automatic matching."*

---

### Q7: "What happens when field reports conflict?"
- **Short Answer**: *SATYA's Evidence & Trust Engine detects contradictory claims (e.g. physical work complete vs QA clearance pending) and flags them as `CONTRADICTORY_EVIDENCE`.*
- **Detailed Explanation**:
  > *"SATYA evaluates claims across independent sources. If Contractor A reports 100% completion but an inspection report indicates QA clearance is pending, SATYA preserves both facts separately. It generates a Trust Assessment with status `REVIEW_REQUIRED` and alerts the Time Agent to trigger a `QA_CLEARANCE_BOTTLENECK` warning."*

---

### Q8: "Can the AI modify the baseline schedule?"
- **Short Answer**: *No. Baseline schedule files are 100% read-only and immutable.*
- **Detailed Explanation**:
  > *"SATYA enforces strict baseline immutability. Baseline dates, planned quantities, and network logic are never altered. SATYA creates separate `ScheduleProjection` records containing actual progress, forecast finish dates, and schedule variance ($SV_{\text{finish}}$), preserving the baseline authority."*

---

### Q9: "How does institutional memory work?"
- **Short Answer**: *Planner corrections are distilled into project-scoped terminology aliases. Memory assists future candidate ranking, but CANNOT force matches or override vocabulary safety.*
- **Detailed Explanation**:
  > *"When a planner re-maps 'HDD Section 3' to `ACT-1020`, SATYA captures this in `InstitutionalMemoryStore`. The alias follows a strict lifecycle: `CANDIDATE` $\rightarrow$ `VALIDATED` $\rightarrow$ `ACTIVE`. Once validated by independent evidence, future occurrences receive an additive boost ($S_{\text{alias}} = +0.25$), allowing future reports to match automatically. However, memory only assists ranking—it can never override closed schedule vocabulary or bypass threshold bounds."*

---

### Q10: "How is the system auditable?"
- **Short Answer**: *All data structures are stored in append-only SQLite tables with full provenance references.*
- **Detailed Explanation**:
  > *"Every `ExecutionEvent` stores its source document ID, line offset, and raw text. When a planner overrides a match, SATYA creates a new Version 2 `TrustAssessment` row while keeping Version 1 completely un-mutated. A judge or auditor can trace any progress number back to its exact cell in a DPR or human decision."*

---

## 2. Enterprise & Production Implementation Questions

### Q11: "How would this integrate with Oil India's existing PMIS or SAP?"
- **Short Answer**: *Via standard REST API endpoints (`backend/api/app.py`) producing JSON payloads compatible with Primavera P6 SDK / SAP Project System.*
- **Detailed Explanation**:
  > *"SATYA exposes clean REST endpoints: `/api/v1/ingestion/upload`, `/api/v1/projections/generate`, and `/api/v1/monitoring/evaluate`. Verified schedule projections can be exported as Primavera XML or pushed via SAP PS BAPIs to update actual progress automatically."*

---

### Q12: "What happens with real Oil India field data (OCR, Assamese/Bilingual text, noisy scans)?"
- **Short Answer**: *Tested resilience against bilingual text, OCR character errors (`1O20` $\rightarrow$ `1020`), and unstructured DPR snippets in our Phase 15 Adversarial Test Suite.*
- **Detailed Explanation**:
  > *"Our Layer 1 text pre-processor includes OCR normalization rules (converting letter 'O' to digit '0' in activity IDs), bilingual noise filtering, and structured regex parsing for pipeline chainages (`KM 14.5`). In Phase 15, we verified structural, linguistic, and adversarial noise resilience across 134 automated tests."*

---

### Q13: "What are the current system limitations?"
- **Short Answer**: *Honest empirical evaluation: Match recall is 49.2% on matchable dev set records, confidence scores act as binary risk-gating thresholds (ECE 0.1783), and downstream trust/forecast layers currently use synthetic dev data.*
- **Detailed Explanation**:
  > *"We take scientific rigor seriously. Our Phase 15 benchmark demonstrated that SATYA achieves **100.0% precision among accepted matches** at $\theta = 0.80$, while conservatively delegating 49.2% of matchable cases to HITL review. Confidence calibration (ECE 0.1783) shows scores cluster near 1.0 or $<0.50$, functioning as a binary safety gate. These are known baseline observations that provide clear technical roadmap items for post-SIH production deployment."*
