# SATYA Matching Engine — Phase 14 Institutional Memory Comparative Benchmark Matrix

> **Document Type:** Ground-Truth Benchmark Audit & Memory Assistance Evaluation Report  
> **Governance Status:** Phase 14 Final Audit Deliverable  

## 1. Comparative Metric Summary: Memory OFF vs Memory ON Across Splits

| Benchmark Split | Memory Mode | Total Recs | Decision Acc | Recall@1 | Recall@3 | Recall@5 | Recall@10 | MRR | NDCG@5 | Matched Coverage | Matched Precision | False Match Rate (Accepted) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **DEVELOPMENT** | `OFF` | 62 | 35.48% | 41.94% | 66.13% | 70.97% | 95.16% | 0.5714 | 0.5837 | 35.48% | 100.0% | 0.0% |
| **DEVELOPMENT** | `ON` | 62 | 35.48% | 41.94% | 66.13% | 70.97% | 95.16% | 0.5714 | 0.5837 | 35.48% | 100.0% | 0.0% |
| **EDGE_CASES** | `OFF` | 5 | 20.0% | 60.0% | 80.0% | 80.0% | 80.0% | 0.6667 | 0.7 | 40.0% | 100.0% | 0.0% |
| **EDGE_CASES** | `ON` | 5 | 20.0% | 60.0% | 80.0% | 80.0% | 80.0% | 0.6667 | 0.7 | 40.0% | 100.0% | 0.0% |
| **EVALUATION** | `OFF` | 40 | 50.0% | 12.5% | 37.5% | 60.0% | 75.0% | 0.3019 | 0.3341 | 0.0% | N/A | N/A |
| **EVALUATION** | `ON` | 40 | 50.0% | 12.5% | 37.5% | 60.0% | 75.0% | 0.3019 | 0.3341 | 0.0% | N/A | N/A |


## 2. Risk–Coverage Policy Sweep (Evaluation Split - 40 Records)

| Confidence Threshold ($\theta_{\text{match}}$) | Matched Coverage | Matched Precision | False Confident Matches | False Match Rate (Accepted) | Uncertainty Rate (HITL) |
| :---: | :---: | :---: | :---: | :---: | :---: |
| **0.60** | 0.0% | N/A | 0 | **N/A** | 100.0% |
| **0.70** | 0.0% | N/A | 0 | **N/A** | 100.0% |
| **0.75** | 0.0% | N/A | 0 | **N/A** | 100.0% |
| **0.80** | 0.0% | N/A | 0 | **N/A** | 100.0% |
| **0.90** | 0.0% | N/A | 0 | **N/A** | 100.0% |


## 3. Failure Taxonomy Breakdown (Memory ON)

| Split | Category | Count | Percentage |
| :--- | :--- | :---: | :---: |
| DEVELOPMENT | `CORRECT_MATCH` | 22 | 35.48% |
| DEVELOPMENT | `RANKING_FAILURE` | 16 | 25.81% |
| DEVELOPMENT | `UNCLASSIFIED_DISCREPANCY` | 20 | 32.26% |
| DEVELOPMENT | `RETRIEVAL_FAILURE` | 3 | 4.84% |
| DEVELOPMENT | `INSUFFICIENT_EVIDENCE` | 1 | 1.61% |
| EDGE_CASES | `CORRECT_UNMATCHED` | 1 | 20.0% |
| EDGE_CASES | `UNCLASSIFIED_DISCREPANCY` | 4 | 80.0% |
| EVALUATION | `ANNOTATION_CONFLICT_OR_GT_AMBIGUITY` | 2 | 5.0% |
| EVALUATION | `CORRECT_AMBIGUITY_DETECTION` | 20 | 50.0% |
| EVALUATION | `RANKING_FAILURE` | 8 | 20.0% |
| EVALUATION | `RETRIEVAL_FAILURE` | 8 | 20.0% |
| EVALUATION | `INSUFFICIENT_EVIDENCE` | 2 | 5.0% |
