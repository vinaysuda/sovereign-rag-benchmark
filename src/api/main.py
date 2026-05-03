from contextlib import asynccontextmanager
from typing import AsyncGenerator
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

from src.core.config import settings
from src.schemas.responses import QueryRequest, RAGResponse
from src.engine.rag_pipeline import orchestrator

# 1. Define the Lifespan Context Manager (Modern replacement for on_event)
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    # --- Startup Logic ---
    print(f"🚀 Starting {settings.api_title} v{settings.api_version}...")
    print("✅ Inference Pipeline & Orchestrator Online.")
    
    yield  # The FastAPI application runs while suspended here
    
    # --- Shutdown Logic ---
    print("🛑 Shutting down Sovereign RAG API...")

# 2. Initialize the FastAPI Application with the lifespan
app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    description="Secure Air-Gapped Document Intelligence API",
    lifespan=lifespan
)

# 3. Configure Cross-Origin Resource Sharing (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict this to your frontend domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 4. The Core Inference Endpoint
@app.post("/api/v1/query", response_model=RAGResponse, tags=["RAG Inference"])
async def process_query(request: QueryRequest) -> RAGResponse:
    """
    Takes a validated user query, orchestrates the retrieval from PostgreSQL,
    and generates an air-gapped LLM response via vLLM.
    """
    try:
        print(f"📥 Received query: '{request.query}'")
        # Hand off to the Orchestrator we built in Phase 3
        response = await orchestrator.generate_answer(request.query)
        return response
    except Exception as e:
        print(f"❌ Error processing query: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal inference engine error")

# 5. Observability Integration
# This automatically instruments every incoming HTTP request and async task
FastAPIInstrumentor.instrument_app(app)