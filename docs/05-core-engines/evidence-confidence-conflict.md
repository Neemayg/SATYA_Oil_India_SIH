# Evidence, Confidence & Conflict Engine Core Specification

> **Document Type:** Core Engine Implementation & Architecture Specification  
> **Governance Status:** Phase 8 Active Deliverable  
> **Project:** SATYA — Oil India Limited (SIH 2026)  

---

## 1. Engine Overview & Core Principles

The **Evidence, Confidence & Conflict Engine** (Phase 8) evaluates extracted `ExecutionEvent` claims against source documents, independent corroboration evidence, discipline-aware evidence policies, and contradictory field records.

It preserves the non-negotiable state separation chain:
$$\text{FIELD REALITY} \rightarrow \text{SOURCE EVIDENCE} \rightarrow \text{EVIDENCE CLAIM} \rightarrow \text{EXECUTION EVENT} \rightarrow \text{SCHEDULE MATCH} \rightarrow \text{EVIDENCE ASSESSMENT} \rightarrow \text{CONFLICT DETECTION} \rightarrow \text{TRUST DECISION} \rightarrow \text{HUMAN VALIDATION} \rightarrow \text{SCHEDULE PROJECTION}$$

```
                [ExecutionEvent]
                        │
                        ▼
                [ClaimExtractor] ────> [EvidenceClaim(s)]
                        │
                        ▼
             [ReliabilityEvaluator] ──> [EvidenceReliabilityAssessment]
                        │
                        ▼
            [CorroborationEngine] ───> [EvidenceAssessment (origin_group_id aware)]
                        │
                        ▼
                 [GapEngine] ────────> [Discipline-Aware Evidence Gaps]
                        │
                        ▼
              [ConflictEngine] ──────> [ConflictFlags (7 Categories)]
                        │
                        ▼
             [TrustEvaluatorService]
                        │ (Deterministic Gating Tree)
        ┌───────────────┼───────────────┐
        ▼               ▼               ▼
    [TRUSTED]   [REVIEW_REQUIRED]  [UNTRUSTED]
```

---

## 2. Three Distinct Confidence Concepts

SATYA explicitly separates matching confidence from evidence quality and trust decisions:

1. **Schedule Match Confidence ($S_{\text{match}}$):** Probabilistic baseline schedule alignment score ($[0.0, 1.0]$) computed by Phase 7 matching engine.
2. **Evidence Support Confidence ($S_{\text{evidence}}$):** Multi-factor score ($[0.0, 1.0]$) evaluating source authority, verification status, provenance completeness, timestamp quality, consistency, and independent corroboration.
3. **Trust Decision ($\text{TrustStatus}$):** Categorical operational state (`TRUSTED`, `REVIEW_REQUIRED`, `UNTRUSTED`), evaluated using a **deterministic gating tree** rather than an opaque weighted formula.

> [!IMPORTANT]
> **Definition of TRUSTED:** `TRUSTED` status indicates that SATYA has sufficient supporting evidence and zero blocking conflicts to treat an execution claim as trusted under the configured policy. It does **NOT** represent an absolute computer-vision physical proof of reality.

---

## 3. Multi-Factor Evidence Reliability Assessment

Evidence reliability is assessed across 5 independent quality dimensions rather than relying solely on source-type rankings:

$$\text{Reliability} = 0.30 \cdot S_{\text{auth}} + 0.20 \cdot S_{\text{verif}} + 0.25 \cdot S_{\text{prov}} + 0.15 \cdot S_{\text{time}} + 0.10 \cdot S_{\text{cons}}$$

| Dimension | Weight | Evaluated Quality Criteria |
| :--- | :---: | :--- |
| **Source Authority ($S_{\text{auth}}$)** | 0.30 | QA/TPIA Inspection (0.95), Site Log (0.75), DPR (0.65), Voice Transcript (0.55), Unknown (0.40) |
| **Verification Status ($S_{\text{verif}}$)** | 0.20 | Verified author metadata (+0.30) & SHA-256 document hash verification (+0.20) |
| **Provenance Completeness ($S_{\text{prov}}$)** | 0.25 | Exact locator available (+0.30) & field-level character spans mapped (+0.30) |
| **Timestamp Quality ($S_{\text{time}}$)** | 0.15 | Explicit date (0.95) vs relative/fallback timestamp (0.40) |
| **Consistency ($S_{\text{cons}}$)** | 0.10 | Coherence and historical agreement with prior logs (0.85) |

---

## 4. Source Independence & Corroboration Modeling

To prevent re-quoted reports (e.g. contractor email quoting contractor DPR) from receiving fake independent corroboration credit, every `Evidence` record tracks an `origin_group_id`:

* `UNCORROBORATED`: 1 evidence item / 1 origin group.
* `CORROBORATED_SAME_ORIGIN`: Multiple fragments sharing identical `origin_group_id`.
* `CORROBORATED_INDEPENDENT`: 2+ distinct `origin_group_id` records (e.g. DPR origin + Independent QA Inspection origin).

---

## 5. Explicit Conflict Taxonomy & Severity Precedence

| Conflict Type | Severity Precedence | Trigger & Blocking Effect |
| :--- | :---: | :--- |
| `QA_CONFLICT` | **CRITICAL** | Contractor reports 100% complete, but QA status is `REJECTED`. 🔴 Blocks `TRUSTED`. |
| `STATUS_CONFLICT` | **HIGH** | Conflicting completion claims ($>40\%$ status variance) on same timestamp. 🔴 Blocks `TRUSTED`. |
| `QUANTITY_CONFLICT` | **HIGH** | Quantity variance exceeds policy threshold ($>15.0\%$). 🔴 Blocks `TRUSTED`. |
| `LOCATION_CONFLICT` | **HIGH** | Conflicting chainages or work front locators for same activity. 🟠 Triggers `REVIEW_REQUIRED`. |
| `SCHEDULE_CONFLICT` | **MEDIUM** | Out-of-sequence execution (predecessor incomplete). 🟡 Triggers `REVIEW_REQUIRED`. |
| `TEMPORAL_CONFLICT` | **MEDIUM** | Claim execution date discrepancy ($>1.0$ day). Evaluates `observed_timestamp`, NOT submission latency. |
| `DUPLICATE_CONFLICT` | **HIGH** | Contradictory text in duplicate submissions across sources. 🟠 Triggers `REVIEW_REQUIRED`. |
| `DUPLICATE_EVIDENCE` | **LOW** | Benign duplicate re-submission across channels. Informational. |

---

## 6. Deterministic Gating Tree for Trust Decisions

```
                  MATCH SUFFICIENT? (S_match >= DEFAULT_MATCH_THRESHOLD)
                        /                     \
                      NO                       YES
                       ↓                        ↓
                   UNTRUSTED            EVIDENCE SUFFICIENT? (S_evidence >= DEFAULT_EVIDENCE_THRESHOLD)
                                              /                      \
                                            NO                        YES
                                             ↓                         ↓
                                      REVIEW_REQUIRED          CRITICAL CONFLICT PRESENT?
                                                                      /         \
                                                                    YES          NO
                                                                     ↓            ↓
                                                                  REVIEW       TRUSTED
```

* Initial Configurable Policy Defaults: `DEFAULT_MATCH_THRESHOLD = 0.75`, `DEFAULT_EVIDENCE_THRESHOLD = 0.60`.

---

## 7. UI Rationale Presentation Format

```text
TRUST ASSESSMENT
────────────────────────────────────────────────────
Schedule Match Confidence: 91.0%
Evidence Support Score:    84.0%
Source Reliability Tier:   HIGH (QA_REPORT + DPR)
Corroboration Status:      CORROBORATED_INDEPENDENT (2 unique origins)
Conflicts Detected:        None
Evidence Gaps:             None

                       ↓

           TRUST STATUS: 🟢 TRUSTED
```
