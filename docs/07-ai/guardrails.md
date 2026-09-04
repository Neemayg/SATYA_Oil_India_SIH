# AI Guardrails & Safety Enforcement Specification

> **Document Type:** AI Guardrail Specification  
> **Governance Status:** Phase 5 Implementation Deliverable  
> **Project:** SATYA — Oil India Limited (SIH 2026)  

---

## 1. Closed-Vocabulary Activity ID Guardrail (Rule 5)

SATYA enforces a hard dictionary guardrail preventing the AI model from inventing or fabricating schedule `Activity ID`s.

```
[Extracted Observed Activity ID]
               │
               ▼
[Is ID in Active Baseline Schedule Vocabulary?]
               │
        ┌──────┴──────┐
        ▼             ▼
      (YES)          (NO)
        │             │
        ▼             ▼
   [Retain ID]   [Set ID = None]
                 [Log Quarantine Warning]
```

---

## 2. Rejection of Invalid Output

Any model payload failing strict JSON schema checks, containing negative quantities, or asserting future dates ($> 24\text{h}$) is routed to `QuarantineRecord` and prevented from entering the trusted ledger.
