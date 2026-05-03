import time
from typing import List
from llama_index.core import VectorStoreIndex, Settings as LlamaIndexSettings
from llama_index.vector_stores.postgres import PGVectorStore
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.openai_like import OpenAILike

from src.core.config import settings
from src.schemas.responses import RAGResponse, SourceNode

class SovereignRAGOrchestrator:
    def __init__(self) -> None:
        print("⚙️ Initializing Sovereign RAG Orchestrator...")
        
        # 1. Initialize the LLM (Pointing to our air-gapped vLLM container)
        self.llm = OpenAILike(
            api_base=settings.vllm_base_url,
            api_key="sk-no-key-required",  # vLLM acts as a local drop-in replacement
            model=settings.llm_model_name,
            is_chat_model=True,
            max_tokens=512,
            temperature=0.1,  # Keep it highly deterministic for regulatory docs
        )
        
        # 2. Initialize the Local Embedding Model
        self.embed_model = HuggingFaceEmbedding(
            model_name=settings.embed_model_name
        )

        # Register models globally within LlamaIndex
        LlamaIndexSettings.llm = self.llm
        LlamaIndexSettings.embed_model = self.embed_model

        # 3. Connect to the pgvector Database
        self.vector_store = PGVectorStore.from_params(
            database=settings.postgres_db,
            host=settings.postgres_host,
            password=settings.postgres_password,
            port=settings.postgres_port,
            user=settings.postgres_user,
            table_name="regulatory_docs",
            embed_dim=settings.embed_dimension,
        )

        # 4. Bind the Store to an Async Query Engine
        self.index = VectorStoreIndex.from_vector_store(
            vector_store=self.vector_store
        )
        
        self.query_engine = self.index.as_query_engine(
            similarity_top_k=3,
            use_async=True  # Crucial for FastAPI performance
        )

    async def generate_answer(self, query_text: str) -> RAGResponse:
        """Executes the full RAG pipeline and returns a validated Pydantic model."""
        start_time = time.time()
        
        # This handles the Embedding -> Retrieval -> Generation loop implicitly
        response = await self.query_engine.aquery(query_text)
        
        # Extract and format the sources (Citations)
        sources: List[SourceNode] = []
        for node in response.source_nodes:
            score = node.score if node.score is not None else 0.0
            sources.append(
                SourceNode(
                    file_name=node.metadata.get("file_name", "Unknown"),
                    text_excerpt=node.text[:250] + "...",  # Take a readable snippet
                    relevance_score=round(score, 4)
                )
            )

        processing_time = round((time.time() - start_time) * 1000, 2)

        # 5. Return the strictly validated Pydantic object
        return RAGResponse(
            answer=str(response),
            sources=sources,
            processing_time_ms=processing_time
        )

# Instantiate a single, global orchestrator to be imported by FastAPI
orchestrator = SovereignRAGOrchestrator()