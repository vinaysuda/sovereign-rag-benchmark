from pydantic import BaseModel, Field
from typing import List

class SourceNode(BaseModel):
    """Represents a chunk of text retrieved from the database."""
    file_name: str = Field(..., description="The name of the source document")
    text_excerpt: str = Field(..., description="A snippet of the retrieved text")
    relevance_score: float = Field(..., description="The vector similarity score")

class QueryRequest(BaseModel):
    """The exact JSON payload the user sends to the API."""
    query: str = Field(..., description="The question asked by the user", min_length=3)

class RAGResponse(BaseModel):
    """The strictly validated output from our pipeline."""
    answer: str = Field(..., description="The generated response from the LLM")
    sources: List[SourceNode] = Field(default_factory=list, description="The documents used to generate the answer")
    processing_time_ms: float = Field(..., description="Total time taken in milliseconds")