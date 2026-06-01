

import pandas as pd
import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
from app.config import get_settings
import logging

logger = logging.getLogger(__name__)
settings = get_settings()


def load_faq_data(path: str) -> list[dict]:
    df = pd.read_excel(path)
    df.columns = [c.strip().lower() for c in df.columns]
    df = df.dropna(subset=["question", "answer"])
    return df[["question", "answer"]].to_dict(orient="records")


def get_chroma_client() -> chromadb.PersistentClient:
    return chromadb.PersistentClient(path=settings.chroma_db_path)


def get_embedding_function() -> SentenceTransformerEmbeddingFunction:
    return SentenceTransformerEmbeddingFunction(
        model_name=settings.local_embedding_model
    )


def ingest_faqs(force: bool = False) -> int:
    client = get_chroma_client()
    ef = get_embedding_function()

    existing = [c.name for c in client.list_collections()]

    if settings.chroma_collection_name in existing and not force:
        col = client.get_collection(settings.chroma_collection_name, embedding_function=ef)
        count = col.count()
        if count > 0:
            logger.info("Collection '%s' already has %d documents. Skipping ingestion.", settings.chroma_collection_name, count)
            return count
        logger.info("Collection exists but is empty — re-ingesting.")

    if settings.chroma_collection_name in existing:
        client.delete_collection(settings.chroma_collection_name)

    collection = client.create_collection(
        name=settings.chroma_collection_name,
        embedding_function=ef,
        metadata={"hnsw:space": "cosine"},
    )

    rows = load_faq_data(settings.faq_data_path)
    documents, metadatas, ids = [], [], []
    for i, row in enumerate(rows):
        doc = f"Question: {row['question']}\nAnswer: {row['answer']}"
        documents.append(doc)
        metadatas.append({"question": row["question"], "answer": row["answer"]})
        ids.append(f"faq_{i}")

    batch_size = 100
    for start in range(0, len(documents), batch_size):
        collection.add(
            documents=documents[start : start + batch_size],
            metadatas=metadatas[start : start + batch_size],
            ids=ids[start : start + batch_size],
        )
        logger.info("Ingested batch %d-%d", start, min(start + batch_size, len(documents)))

    logger.info("Ingestion complete — %d FAQ documents stored.", len(documents))
    return len(documents)