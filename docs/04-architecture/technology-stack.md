# Technology Stack & Implementation Selection

> **Document Type:** Implementation Technology Selection  
> **Governance Status:** Phase 5 Deliverable  
> **Project:** SATYA — Oil India Limited (SIH 2026)  

---

## 1. Selected Prototype Technology Stack

For the SATYA SIH 2026 Minimum Viable Product (MVP), the implementation stack is selected to prioritize **simplicity, modularity, zero external operational overhead, and 100% testability**.

```
+-----------------------------------------------------------------------------------+
|                            SATYA TECHNOLOGY STACK                                 |
+-----------------------------------------------------------------------------------+
|  Programming Language  : Python 3.13 (Standard Library + Standard Modules)        |
|  Architecture Model    : Modular Monolith (Decoupled Package Boundaries)          |
|  Database / Ledger     : SQLite (ACID Relational Engine with Append-Only Tables)  |
|  Testing Framework     : Python `unittest` Standard Library                       |
|  Serialization / Schema: Standard JSON & Python Data Structures                   |
|  Deployment Environment: Cross-Platform Local Execution (macOS / Linux / Windows)   |
+-----------------------------------------------------------------------------------+
```

---

## 2. Rationale & Trade-Off Analysis

* **Python 3.13 Core:** Chosen for native support for data manipulation, structured parsing, pattern matching, built-in SQLite engine, and zero-dependency portability.
* **SQLite Persistence Engine:** Provides lightweight, ACID-compliant relational storage supporting append-only transaction logs. Eliminates the need for running external database daemons during prototype development.
* **Modular Monolith Design:** Enforces strict package separation (`ingestion`, `normalization`, `extraction`, `validation`, `persistence`) without introducing microservices network latency, message queues, or Kubernetes overhead.
* **Standard Library Testing (`unittest`):** Guarantees zero installation friction and fast, deterministic test suite execution.

---

## 3. Prohibited Technologies in Phase 5

* **No Microservices Frameworks** (gRPC, Celery, RabbitMQ)
* **No Vector Databases** (ChromaDB, Pinecone, Qdrant)
* **No Heavy OCR / Speech Engines** (Tesseract, Whisper)
* **No Complex LLM Orchestration Frameworks** (LangChain, LlamaIndex)
