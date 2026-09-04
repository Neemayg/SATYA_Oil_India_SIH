# AI Extraction Pipeline Evaluation Framework

> **Document Type:** Evaluation Framework  
> **Governance Status:** Phase 5 Implementation Deliverable  
> **Project:** SATYA — Oil India Limited (SIH 2026)  

---

## 1. Benchmark Datasets

The extraction pipeline is evaluated against the synthetic datasets created in Phase 4:
* `data/synthetic/ground-truth/ground_truth_dev.json` (62 records)
* `data/synthetic/ground-truth/ground_truth_eval.json` (40 records)
* `data/synthetic/ground-truth/ground_truth_edge_cases.json` (5 records)

---

## 2. Core Evaluation Metrics

1. **Entity Extraction Precision:** % of extracted work actions, quantities, and units matching ground truth.
2. **Rule 5 Compliance Rate:** % of invalid/hallucinated Activity IDs correctly blocked ($100\%$ target).
3. **Quarantine Surface Recall:** % of invalid or impossible input records correctly routed to Quarantine ($100\%$ target).
