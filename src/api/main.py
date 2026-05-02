from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from langfuse.llama_index import LlamaIndexInstrumentor

# FIX: Import the correct, updated engine function
from src.engine.rag_pipeline import configure_engine, get_hybrid_query_engine
from src.schemas.responses import ComplianceResponse

app = FastAPI(
    title="Sovereign RAG Benchmark",
    description="Air-gapped compliance query engine.",
    version="1.0.0",
)

# Instrument Langfuse for RAG Tracing
langfuse_instrumentor = LlamaIndexInstrumentor()
langfuse_instrumentor.start()


class QueryRequest(BaseModel):
    query: str


@app.on_event("startup")
def startup_event() -> None:  # FIX: Explicit return type
    configure_engine()


@app.post("/api/v1/query", response_model=ComplianceResponse)
async def query_compliance_docs(
    payload: QueryRequest,
) -> ComplianceResponse:  # FIX: Explicit return type
    try:
        # Fetch our heavily filtered query engine
        query_engine = get_hybrid_query_engine()

        # Execute the query
        response = query_engine.query(payload.query)

        # Format the response to strictly match our Pydantic schema
        # (In a true production environment, you would map the LlamaIndex source nodes here)
        return ComplianceResponse(answer=str(response), citations=[], confidence_indicator="High")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Instrument FastAPI for latency profiling (OpenTelemetry)
FastAPIInstrumentor.instrument_app(app)
