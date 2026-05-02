import asyncio
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex, StorageContext
from src.engine.rag_pipeline import configure_engine, get_vector_store


async def run_async_ingestion(data_dir: str = "data/raw") -> None:
    """
    Simulates the Redis-backed async chunking queue.
    In production, this processes the 500,000+ document corpus from Azure Blob Storage.
    """
    # 1. Boot up the local models
    configure_engine()

    print(f"Loading raw regulatory documents from {data_dir}...")
    try:
        documents = SimpleDirectoryReader(data_dir).load_data()
    except ValueError:
        print(f"Warning: No documents found in {data_dir}. Place sample PDFs/TXTs here to test.")
        return

    # 2. Add strict metadata to simulate regulatory tagging
    for doc in documents:
        doc.metadata["jurisdiction"] = "EASA"
        doc.metadata["doc_type"] = "Airworthiness Directive"

    # 3. Connect to pgvector
    vector_store = get_vector_store()
    storage_context = StorageContext.from_defaults(vector_store=vector_store)

    print(f"Asynchronously embedding and indexing {len(documents)} document chunks...")

    # 4. Asynchronous batch ingestion
    VectorStoreIndex.from_documents(
        documents,
        storage_context=storage_context,
        show_progress=True,
        use_async=True,  # Parallelizes embedding calls to Hugging Face
    )

    print("Ingestion complete. Vector store optimized.")


if __name__ == "__main__":
    asyncio.run(run_async_ingestion())
