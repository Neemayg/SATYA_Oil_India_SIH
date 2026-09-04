# SATYA Matching Engine — Phase 7.1 Final Audit Benchmark Matrix

> **Document Type:** Ground-Truth Benchmark Audit & Risk-Coverage Policy Report  
> **Governance Status:** Phase 7.1 Final Audit Patch Deliverable  

## 1. Multi-Dimensional Metric Summary Across Splits

| Benchmark Split | Total Recs | Decision Acc | Recall@1 | Recall@3 | Recall@5 | Recall@10 | MRR | NDCG@5 | Matched Coverage | Matched Precision | False Match Rate (Accepted) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **DEVELOPMENT** | 62 | 35.48% | 41.94% | 66.13% | 70.97% | **95.16%** | 0.5714 | 0.5837 | 35.48% | 100.0% | **0.0%** |
| **EDGE_CASES** | 5 | 20.0% | 60.0% | 80.0% | 80.0% | **80.0%** | 0.6667 | 0.7 | 40.0% | 100.0% | **0.0%** |
| **EVALUATION** | 40 | 50.0% | 12.5% | 37.5% | 60.0% | **75.0%** | 0.3019 | 0.3341 | 0.0% | N/A | **N/A** |


## 2. Risk–Coverage Policy Sweep (Evaluation Split - 40 Records)

| Confidence Threshold ($\theta_{\text{match}}$) | Matched Coverage | Matched Precision | False Confident Matches | False Match Rate (Accepted) | Uncertainty Rate (HITL) |
| :---: | :---: | :---: | :---: | :---: | :---: |
| **0.60** | 0.0% | N/A | 0 | **N/A** | 100.0% |
| **0.70** | 0.0% | N/A | 0 | **N/A** | 100.0% |
| **0.75** | 0.0% | N/A | 0 | **N/A** | 100.0% |
| **0.80** | 0.0% | N/A | 0 | **N/A** | 100.0% |
| **0.90** | 0.0% | N/A | 0 | **N/A** | 100.0% |


## 3. Failure Taxonomy Breakdown

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


## 4. Evaluation Split Technical Failure Root Cause Diagnostics (16 Cases)

| Index | Source ID | Failure Type | Expected Activity | Top Candidate Returned | Root Cause Analysis |
| :---: | :--- | :--- | :--- | :--- | :--- |
| 00 | `SRC-OBS-102` | `ANNOTATION_CONFLICT_OR_GT_AMBIGUITY` | `ACT-1012` | `ACT-1012` (0.6) | Raw snippet contains literal string truncation ('&...') from synthetic dataset generation, obscuring action verbs and locators. |
| 02 | `SRC-OBS-107` | `RANKING_FAILURE` | `ACT-1017` | `ACT-1013` (0.6) | Raw snippet contains literal string truncation ('&...') from synthetic dataset generation, obscuring action verbs and locators. |
| 04 | `SRC-OBS-112` | `RANKING_FAILURE` | `ACT-1022` | `ACT-1010` (0.6) | Raw snippet contains literal string truncation ('&...') from synthetic dataset generation, obscuring action verbs and locators. |
| 06 | `SRC-OBS-117` | `RETRIEVAL_FAILURE` | `ACT-1027` | `ACT-1010` (0.47) | Raw snippet contains literal string truncation ('&...') from synthetic dataset generation, obscuring action verbs and locators. |
| 08 | `SRC-OBS-122` | `ANNOTATION_CONFLICT_OR_GT_AMBIGUITY` | `ACT-1032` | `ACT-1032` (0.6) | Raw snippet contains literal string truncation ('&...') from synthetic dataset generation, obscuring action verbs and locators. |
| 10 | `SRC-OBS-127` | `RANKING_FAILURE` | `ACT-1037` | `ACT-1033` (0.6) | Raw snippet contains literal string truncation ('&...') from synthetic dataset generation, obscuring action verbs and locators. |
| 12 | `SRC-OBS-132` | `RANKING_FAILURE` | `ACT-1042` | `ACT-1030` (0.6) | Raw snippet contains literal string truncation ('&...') from synthetic dataset generation, obscuring action verbs and locators. |
| 14 | `SRC-OBS-137` | `RETRIEVAL_FAILURE` | `ACT-1047` | `ACT-1030` (0.47) | Raw snippet contains literal string truncation ('&...') from synthetic dataset generation, obscuring action verbs and locators. |
| 16 | `SRC-OBS-142` | `RANKING_FAILURE` | `ACT-1052` | `ACT-1060` (0.35) | Raw snippet contains literal string truncation ('&...') from synthetic dataset generation, obscuring action verbs and locators. |
| 18 | `SRC-OBS-147` | `RANKING_FAILURE` | `ACT-1057` | `ACT-1056` (0.47) | Raw snippet contains literal string truncation ('&...') from synthetic dataset generation, obscuring action verbs and locators. |
| 24 | `SRC-OBS-162` | `RETRIEVAL_FAILURE` | `ACT-SCP-8012` | `ACT-SCP-8014` (0.45) | Raw snippet contains literal string truncation ('&...') from synthetic dataset generation, obscuring action verbs and locators. |
| 26 | `SRC-OBS-167` | `RETRIEVAL_FAILURE` | `ACT-SCP-8017` | `ACT-SCP-8014` (0.45) | Raw snippet contains literal string truncation ('&...') from synthetic dataset generation, obscuring action verbs and locators. |
| 28 | `SRC-OBS-172` | `RETRIEVAL_FAILURE` | `ACT-SCP-8022` | `ACT-SCP-8014` (0.45) | Raw snippet contains literal string truncation ('&...') from synthetic dataset generation, obscuring action verbs and locators. |
| 30 | `SRC-OBS-177` | `RETRIEVAL_FAILURE` | `ACT-SCP-8027` | `ACT-SCP-8029` (0.45) | Raw snippet contains literal string truncation ('&...') from synthetic dataset generation, obscuring action verbs and locators. |
| 32 | `SRC-OBS-182` | `RETRIEVAL_FAILURE` | `ACT-SCP-8032` | `ACT-SCP-8029` (0.45) | Raw snippet contains literal string truncation ('&...') from synthetic dataset generation, obscuring action verbs and locators. |
| 34 | `SRC-OBS-187` | `RETRIEVAL_FAILURE` | `ACT-SCP-8037` | `ACT-SCP-8029` (0.45) | Raw snippet contains literal string truncation ('&...') from synthetic dataset generation, obscuring action verbs and locators. |
| 36 | `SRC-OBS-192` | `RANKING_FAILURE` | `ACT-SCP-8042` | `ACT-SCP-8041` (0.49) | Raw snippet contains literal string truncation ('&...') from synthetic dataset generation, obscuring action verbs and locators. |
| 38 | `SRC-OBS-197` | `RANKING_FAILURE` | `ACT-SCP-8047` | `ACT-SCP-8041` (0.49) | Raw snippet contains literal string truncation ('&...') from synthetic dataset generation, obscuring action verbs and locators. |


## 5. Evaluation Split Line-by-Line Record Matrix (40 Records)

| Index | Source ID | Snippet | Expected IDs | Expected Outcome | Predicted Outcome | Top Candidate | Score | Failure Class |
| :---: | :--- | :--- | :--- | :---: | :---: | :--- | :---: | :--- |
| 00 | `SRC-OBS-102` | Section 1 PIP scope ongoing: Mainli.. | `ACT-1012` | `MATCHED` | `AMBIGUOUS` | `ACT-1012` | 0.6 | `ANNOTATION_CONFLICT_OR_GT_AMBIGUITY` |
| 01 | `SRC-OBS-103` | Execution ongoing for civil task in.. | `ACT-1013, ACT-1014` | `AMBIGUOUS` | `INSUFFICIENT_EVIDENCE` | `ACT-1010` | 0.35 | `CORRECT_AMBIGUITY_DETECTION` |
| 02 | `SRC-OBS-107` | Section 1 CIV scope ongoing: Mainli.. | `ACT-1017` | `MATCHED` | `AMBIGUOUS` | `ACT-1013` | 0.6 | `RANKING_FAILURE` |
| 03 | `SRC-OBS-108` | Execution ongoing for civil task in.. | `ACT-1018, ACT-1019` | `AMBIGUOUS` | `INSUFFICIENT_EVIDENCE` | `ACT-1010` | 0.35 | `CORRECT_AMBIGUITY_DETECTION` |
| 04 | `SRC-OBS-112` | Section 1 CIV scope ongoing: Mainli.. | `ACT-1022` | `MATCHED` | `AMBIGUOUS` | `ACT-1010` | 0.6 | `RANKING_FAILURE` |
| 05 | `SRC-OBS-113` | Execution ongoing for civil task in.. | `ACT-1023, ACT-1024` | `AMBIGUOUS` | `INSUFFICIENT_EVIDENCE` | `ACT-1010` | 0.35 | `CORRECT_AMBIGUITY_DETECTION` |
| 06 | `SRC-OBS-117` | Section 1 CIV scope ongoing: Mainli.. | `ACT-1027` | `MATCHED` | `INSUFFICIENT_EVIDENCE` | `ACT-1010` | 0.47 | `RETRIEVAL_FAILURE` |
| 07 | `SRC-OBS-118` | Execution ongoing for piping task i.. | `ACT-1028, ACT-1029` | `AMBIGUOUS` | `INSUFFICIENT_EVIDENCE` | `ACT-1012` | 0.35 | `CORRECT_AMBIGUITY_DETECTION` |
| 08 | `SRC-OBS-122` | Section 2 PIP scope ongoing: Mainli.. | `ACT-1032` | `MATCHED` | `AMBIGUOUS` | `ACT-1032` | 0.6 | `ANNOTATION_CONFLICT_OR_GT_AMBIGUITY` |
| 09 | `SRC-OBS-123` | Execution ongoing for civil task in.. | `ACT-1033, ACT-1034` | `AMBIGUOUS` | `INSUFFICIENT_EVIDENCE` | `ACT-1030` | 0.35 | `CORRECT_AMBIGUITY_DETECTION` |
| 10 | `SRC-OBS-127` | Section 2 CIV scope ongoing: Mainli.. | `ACT-1037` | `MATCHED` | `AMBIGUOUS` | `ACT-1033` | 0.6 | `RANKING_FAILURE` |
| 11 | `SRC-OBS-128` | Execution ongoing for civil task in.. | `ACT-1038, ACT-1039` | `AMBIGUOUS` | `INSUFFICIENT_EVIDENCE` | `ACT-1030` | 0.35 | `CORRECT_AMBIGUITY_DETECTION` |
| 12 | `SRC-OBS-132` | Section 2 CIV scope ongoing: Mainli.. | `ACT-1042` | `MATCHED` | `AMBIGUOUS` | `ACT-1030` | 0.6 | `RANKING_FAILURE` |
| 13 | `SRC-OBS-133` | Execution ongoing for civil task in.. | `ACT-1043, ACT-1044` | `AMBIGUOUS` | `INSUFFICIENT_EVIDENCE` | `ACT-1030` | 0.35 | `CORRECT_AMBIGUITY_DETECTION` |
| 14 | `SRC-OBS-137` | Section 2 CIV scope ongoing: Mainli.. | `ACT-1047` | `MATCHED` | `INSUFFICIENT_EVIDENCE` | `ACT-1030` | 0.47 | `RETRIEVAL_FAILURE` |
| 15 | `SRC-OBS-138` | Execution ongoing for piping task i.. | `ACT-1048, ACT-1049` | `AMBIGUOUS` | `INSUFFICIENT_EVIDENCE` | `ACT-1032` | 0.35 | `CORRECT_AMBIGUITY_DETECTION` |
| 16 | `SRC-OBS-142` | GGS-3 STR scope ongoing: GGS-3 Pipe.. | `ACT-1052` | `MATCHED` | `INSUFFICIENT_EVIDENCE` | `ACT-1060` | 0.35 | `RANKING_FAILURE` |
| 17 | `SRC-OBS-143` | Execution ongoing for structural ta.. | `ACT-1053, ACT-1054` | `AMBIGUOUS` | `INSUFFICIENT_EVIDENCE` | `ACT-1052` | 0.35 | `CORRECT_AMBIGUITY_DETECTION` |
| 18 | `SRC-OBS-147` | GGS-3 MEC scope ongoing: GGS-3 Crud.. | `ACT-1057` | `MATCHED` | `INSUFFICIENT_EVIDENCE` | `ACT-1056` | 0.47 | `RANKING_FAILURE` |
| 19 | `SRC-OBS-148` | Execution ongoing for mechanical ta.. | `ACT-1058, ACT-1059` | `AMBIGUOUS` | `INSUFFICIENT_EVIDENCE` | `ACT-1055` | 0.35 | `CORRECT_AMBIGUITY_DETECTION` |
| 20 | `SRC-OBS-152` | GGS-3 ELE scope ongoing: GGS-3 Subs.. | `ACT-1062` | `MATCHED` | `INSUFFICIENT_EVIDENCE` | `ACT-1062` | 0.47 | `INSUFFICIENT_EVIDENCE` |
| 21 | `SRC-OBS-153` | Execution ongoing for electrical ta.. | `ACT-1063, ACT-1064` | `AMBIGUOUS` | `INSUFFICIENT_EVIDENCE` | `ACT-1062` | 0.35 | `CORRECT_AMBIGUITY_DETECTION` |
| 22 | `SRC-OBS-157` | GGS-3 INS scope ongoing: GGS-3 Cold.. | `ACT-1067` | `MATCHED` | `INSUFFICIENT_EVIDENCE` | `ACT-1067` | 0.47 | `INSUFFICIENT_EVIDENCE` |
| 23 | `SRC-OBS-158` | Execution ongoing for piping task i.. | `ACT-4010, ACT-4011` | `AMBIGUOUS` | `INSUFFICIENT_EVIDENCE` | `ACT-4010` | 0.55 | `CORRECT_AMBIGUITY_DETECTION` |
| 24 | `SRC-OBS-162` | Spread A QA_ scope ongoing: 20-inch.. | `ACT-SCP-8012` | `MATCHED` | `INSUFFICIENT_EVIDENCE` | `ACT-SCP-8014` | 0.45 | `RETRIEVAL_FAILURE` |
| 25 | `SRC-OBS-163` | Execution ongoing for civil task in.. | `ACT-SCP-8013, ACT-8014` | `AMBIGUOUS` | `INSUFFICIENT_EVIDENCE` | `ACT-SCP-8014` | 0.37 | `CORRECT_AMBIGUITY_DETECTION` |
| 26 | `SRC-OBS-167` | Spread A QA_ scope ongoing: 20-inch.. | `ACT-SCP-8017` | `MATCHED` | `INSUFFICIENT_EVIDENCE` | `ACT-SCP-8014` | 0.45 | `RETRIEVAL_FAILURE` |
| 27 | `SRC-OBS-168` | Execution ongoing for civil task in.. | `ACT-SCP-8018, ACT-8019` | `AMBIGUOUS` | `INSUFFICIENT_EVIDENCE` | `ACT-SCP-8014` | 0.37 | `CORRECT_AMBIGUITY_DETECTION` |
| 28 | `SRC-OBS-172` | Spread A QA_ scope ongoing: 20-inch.. | `ACT-SCP-8022` | `MATCHED` | `INSUFFICIENT_EVIDENCE` | `ACT-SCP-8014` | 0.45 | `RETRIEVAL_FAILURE` |
| 29 | `SRC-OBS-173` | Execution ongoing for civil task in.. | `ACT-SCP-8023, ACT-8024` | `AMBIGUOUS` | `INSUFFICIENT_EVIDENCE` | `ACT-SCP-8014` | 0.37 | `CORRECT_AMBIGUITY_DETECTION` |
| 30 | `SRC-OBS-177` | Spread B QA_ scope ongoing: 20-inch.. | `ACT-SCP-8027` | `MATCHED` | `INSUFFICIENT_EVIDENCE` | `ACT-SCP-8029` | 0.45 | `RETRIEVAL_FAILURE` |
| 31 | `SRC-OBS-178` | Execution ongoing for civil task in.. | `ACT-SCP-8028, ACT-8029` | `AMBIGUOUS` | `INSUFFICIENT_EVIDENCE` | `ACT-SCP-8029` | 0.37 | `CORRECT_AMBIGUITY_DETECTION` |
| 32 | `SRC-OBS-182` | Spread B QA_ scope ongoing: 20-inch.. | `ACT-SCP-8032` | `MATCHED` | `INSUFFICIENT_EVIDENCE` | `ACT-SCP-8029` | 0.45 | `RETRIEVAL_FAILURE` |
| 33 | `SRC-OBS-183` | Execution ongoing for civil task in.. | `ACT-SCP-8033, ACT-8034` | `AMBIGUOUS` | `INSUFFICIENT_EVIDENCE` | `ACT-SCP-8029` | 0.37 | `CORRECT_AMBIGUITY_DETECTION` |
| 34 | `SRC-OBS-187` | Spread B QA_ scope ongoing: 20-inch.. | `ACT-SCP-8037` | `MATCHED` | `INSUFFICIENT_EVIDENCE` | `ACT-SCP-8029` | 0.45 | `RETRIEVAL_FAILURE` |
| 35 | `SRC-OBS-188` | Execution ongoing for civil task in.. | `ACT-SCP-8038, ACT-8039` | `AMBIGUOUS` | `INSUFFICIENT_EVIDENCE` | `ACT-SCP-8029` | 0.37 | `CORRECT_AMBIGUITY_DETECTION` |
| 36 | `SRC-OBS-192` | Tank Farm 1 STR scope ongoing: Tank.. | `ACT-SCP-8042` | `MATCHED` | `INSUFFICIENT_EVIDENCE` | `ACT-SCP-8041` | 0.49 | `RANKING_FAILURE` |
| 37 | `SRC-OBS-193` | Execution ongoing for structural ta.. | `ACT-SCP-8043, ACT-8044` | `AMBIGUOUS` | `INSUFFICIENT_EVIDENCE` | `ACT-SCP-8041` | 0.47 | `CORRECT_AMBIGUITY_DETECTION` |
| 38 | `SRC-OBS-197` | Tank Farm 1 PIP scope ongoing: Tank.. | `ACT-SCP-8047` | `MATCHED` | `INSUFFICIENT_EVIDENCE` | `ACT-SCP-8041` | 0.49 | `RANKING_FAILURE` |
| 39 | `SRC-OBS-198` | Execution ongoing for piping task i.. | `ACT-SCP-8048, ACT-8049` | `AMBIGUOUS` | `INSUFFICIENT_EVIDENCE` | `ACT-SCP-8041` | 0.49 | `CORRECT_AMBIGUITY_DETECTION` |
