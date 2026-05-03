import os
import asyncio
import redis
from llama_index.core import SimpleDirectoryReader
from llama_index.core.node_parser import SentenceSplitter
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.vector_stores.postgres import PGVectorStore
from llama_index.core.ingestion import IngestionPipeline

async def main() -> None:
    print("🚀 Initializing Sovereign RAG Ingestion Worker...")

    # 1. Connect to Redis Queue (Deduplication / Job State)
    print("Connecting to Redis...")
    redis_client = redis.Redis(host="localhost", port=6379, decode_responses=True)

    # 2. Initialize the Local Hugging Face Embedding Model (Air-gapped)
    # Using BAAI/bge-small-en-v1.5 as it is incredibly fast and highly rated for RAG
    print("Loading HF Embeddings...")
    embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")

    # 3. Connect to the PostgreSQL + pgvector database
    print("Connecting to pgvector...")
    vector_store = PGVectorStore.from_params(
        database="sovereign_rag",
        host="localhost",
        password="secure_password_here",
        port="5432",
        user="admin",
        table_name="regulatory_docs",
        embed_dim=384,  # Must match the output dimension of the BAAI model
        # async_driver=True - Removed as LlamaIndex handles async automatically
    )

    # 4. Set up the LlamaIndex Ingestion Pipeline
    pipeline = IngestionPipeline(
        transformations=[
            SentenceSplitter(chunk_size=256, chunk_overlap=20),
            embed_model,
        ],
        vector_store=vector_store,
    )

    # 5. Read and Queue Raw Documents
    print("Scanning 'data/' for new documents...")
    all_docs = SimpleDirectoryReader("data/raw").load_data()
    docs_to_process = []

    for doc in all_docs:
        # Check Redis to see if we have already ingested this exact file
        file_name = doc.metadata.get("file_name", "unknown")
        if not redis_client.exists(f"processed:{file_name}"):
            docs_to_process.append(doc)
        else:
            print(f"⏭️ Skipping {file_name} (Already in Redis queue)")

    if not docs_to_process:
        print("✅ No new documents to ingest.")
        return

    # 6. Run the Pipeline (Parse -> Chunk -> Embed -> Insert)
    print(f"Processing {len(docs_to_process)} new document(s). Downloading model weights if first run...")
    nodes = await pipeline.arun(documents=docs_to_process)
    
    # 7. Mark as complete in Redis
    for doc in docs_to_process:
        file_name = doc.metadata.get("file_name", "unknown")
        redis_client.set(f"processed:{file_name}", "done")

    print(f"✅ Successfully batch-inserted {len(nodes)} vector chunks into PostgreSQL!")

if __name__ == "__main__":
    # Ensure the code runs via the async event loop
    asyncio.run(main())