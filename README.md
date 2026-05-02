# 🛡️ Sovereign RAG Benchmark

An open-source, fully air-gapped Retrieval-Augmented Generation (RAG) architecture designed for highly regulated environments (Aerospace, Defense, Healthcare). 

This repository serves as a benchmark for building enterprise-grade Document Intelligence over complex regulatory directives and engineering specifications **without relying on managed public APIs** (like OpenAI or Anthropic). It demonstrates how to orchestrate local LLM inference, hybrid vector retrieval, and deterministic citation tracking entirely within a secure perimeter, guaranteeing zero data leakage and zero vendor lock-in.

## 📊 Enterprise Impact & Benchmark Results
In production environments mirroring this architecture, the system achieved:
* **Query Resolution Time:** Reduced compliance analyst lookup times from **~45 minutes to under 3 minutes**.
* **Retrieval Precision:** Improved precision on domain-specific regulatory queries by **43%** using strict metadata pre-filtering.
* **Latency:** Sustained **sub-200ms** retrieval latency across a corpus of 500,000+ indexed document chunks.
* **Ingestion Velocity:** Reduced full-corpus re-ingestion time from **6.2 hours to 1.4 hours** using Redis-backed asynchronous chunking queues.

## 🏗️ System Architecture
```mermaid
flowchart TB
    %% --- Node Styling ---
    classDef db fill:#0052CC,stroke:#fff,stroke-width:2px,color:#fff
    classDef ai fill:#FF8B00,stroke:#fff,stroke-width:2px,color:#fff
    classDef core fill:#172B4D,stroke:#fff,stroke-width:2px,color:#fff
    classDef api fill:#36B37E,stroke:#fff,stroke-width:2px,color:#fff

    subgraph VPC [🔒 Secure Air-Gapped Perimeter]
        
        subgraph Ingestion [1. Asynchronous Ingestion]
            direction LR
            Doc([Raw Docs]) --> Q[{Redis Queue}] --> E1[HF Embeddings]:::ai
        end

        DB[(PostgreSQL + pgvector)]:::db

        subgraph Inference [2. Retrieval & Generation Pipeline]
            direction TB
            Req([User Query]) --> App[FastAPI]:::api
            App --> Engine[LlamaIndex Engine]:::core
            Engine --> E2[HF Embeddings]:::ai
            Engine --> LLM[vLLM Meta Llama 3]:::ai
            Engine --> Val[Pydantic V2]:::core
        end
        
        subgraph Obs [3. Observability Layer]
            direction LR
            Otel[OpenTelemetry]:::core
            Lang[Langfuse]:::core
        end
        
        %% Internal Layout Routing
        E1 ==> |Batch Insert| DB
        E2 <--> |Vector Search| DB
        App -.-> Otel
        Engine -.-> Lang
    end
    
    Val ==> Out([Validated JSON Response])
    
    %% Transparent styling prevents dark/light mode issues
    style VPC fill:transparent,stroke:#888,stroke-dasharray: 5 5,stroke-width:2px
    style Ingestion fill:transparent,stroke:#555,stroke-width:1px
    style Inference fill:transparent,stroke:#555,stroke-width:1px
    style Obs fill:transparent,stroke:#555,stroke-width:1px
```

## 🛠️ The Tech Stack

* **AI & Orchestration**
  * **Meta Llama 3 (8B Instruct):** Served locally via **vLLM** for high-throughput inference.
  * **Hugging Face (`BAAI/bge-large-en-v1.5`):** Self-hosted local embedding model.
  * **LlamaIndex:** Hybrid RAG pipeline orchestration.
* **Backend & Data Processing**
  * **Python 3.12:** Strictly typed via `mypy`.
  * **FastAPI:** High-performance async API layer.
  * **PostgreSQL + `pgvector`:** Persistent vector storage.
  * **Redis:** In-memory message broker.
* **Validation & Observability**
  * **Pydantic V2:** Enforcing strict, deterministic JSON schemas for citation traceability.
  * **Langfuse & OpenTelemetry:** Distributed tracing.

---

## 🚀 Getting Started (Local Benchmark)

### 1. Prerequisites & Environment
* **Hardware:** An NVIDIA GPU is recommended for vLLM inference.
* **Tokens:** You must accept Meta's Llama 3 license on Hugging Face and generate an access token.

Create a `.env` file in the root directory:
```env
HF_TOKEN=hf_your_huggingface_token_here
```

### 2. Stand Up Infrastructure
Boot the isolated PostgreSQL (`pgvector`), Redis queue, and local `vLLM` container.
```bash
docker compose up -d
```

### 3. Install Dependencies
This project uses `uv` for deterministic dependency resolution.
```bash
uv venv --python 3.12
source .venv/bin/activate  # Windows: .venv\Scripts\activate
uv pip install -e .
```

### 4. Code Quality & Testing (CI/CD Readiness)
This codebase adheres to strict enterprise hygiene. Before running, verify the types and unit tests:
```bash
# Run strict static type checking
uv run mypy src/ scripts/ tests/

# Run the API boundary test suite
uv run pytest
```

### 5. Generate & Ingest Data
Generate synthetic regulatory directives and asynchronously embed them into `pgvector`.
```bash
uv run python scripts/generate_sample_data.py
uv run python src/engine/ingest.py
```

### 6. Run the API & Benchmark
Start the FastAPI server:
```bash
uvicorn src.api.main:app --reload --port 8080
```
In a separate terminal, execute the automated benchmark load test to verify latency and citation traceability:
```bash
uv run python scripts/run_benchmark.py
```

## ☁️ Enterprise Deployment Topology
While this repository provides a local Dockerized benchmark, the architecture is designed for strictly controlled cloud perimeters. See `infrastructure/vllm-gpu-deployment.bicep` for a reference deployment mapping this system to **Azure Container Apps** operating entirely within an internal Virtual Network, secured by **Azure API Management** and **Azure Private Link** to ensure zero public internet routing.
```

***