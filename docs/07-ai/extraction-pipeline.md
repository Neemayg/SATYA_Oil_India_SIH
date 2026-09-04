# AI Entity Extraction Pipeline Architecture

> **Document Type:** AI Engine Specification  
> **Governance Status:** Phase 5 Implementation Deliverable  
> **Project:** SATYA — Oil India Limited (SIH 2026)  

---

## 1. Hybrid Entity Extraction Design

The Phase 5 extraction engine combines deterministic pattern matching with structured entity resolution rules to parse unstructured text snippets into `ExecutionEvent` entities.

```
RAW FRAGMENT TEXT
   │
   ├── Action Verb Matching (START, PROGRESS, FINISH, HOLD, QA_CLEARANCE)
   ├── Discipline Taxonomy Matching (CIVIL, PIPING, STRUCTURAL, MECHANICAL, etc.)
   ├── Numeric Quantity & UOM Regex Parser (180m, 400 meters, 12 joints, 45 MT)
   ├── Location & Chainage Interval Extractor (Km 14.100 - 14.280, Ch 12+400)
   ├── Real-World Fields Extractor (Shift Context, Pending QA, Remaining Qty, Work Front)
   └── Explicit Activity ID Parser (Rule 5 Constrained)
   │
   ▼
[STRUCTURED EXECUTION EVENT]
```

---

## 2. Extraction Confidence Scoring Model

Extraction Confidence ($C_{\text{ext}} \in [0.0, 1.0]$) is computed deterministically:

$$C_{\text{ext}} = 0.40 + 0.15 \cdot \mathbb{I}(\text{EventType}) + 0.15 \cdot \mathbb{I}(\text{Discipline}) + 0.15 \cdot \mathbb{I}(\text{Quantity}) + 0.10 \cdot \mathbb{I}(\text{Location}) + 0.05 \cdot \mathbb{I}(\text{ActivityID})$$

Where $\mathbb{I}(\cdot) = 1$ if the entity was explicitly resolved, and $0$ otherwise.
