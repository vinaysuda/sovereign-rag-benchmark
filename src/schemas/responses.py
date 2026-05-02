from pydantic import BaseModel, Field
from typing import List

class DocumentCitation(BaseModel):
    document_id: str = Field(description="The internal ID or filename of the regulatory document.")
    exact_quote: str = Field(description="The verbatim text chunk used to form the answer.")
    relevance_score: float = Field(description="The pgvector similarity score.")

class ComplianceResponse(BaseModel):
    answer: str = Field(description="The synthesized answer to the regulatory query.")
    citations: List[DocumentCitation] = Field(description="Mandatory array of sources used to generate the answer.")
    confidence_indicator: str = Field(description="High, Medium, or Low based on retrieval density.")