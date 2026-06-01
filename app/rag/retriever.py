

from app.rag.ingestion import get_chroma_client, get_embedding_function
from app.config import get_settings

settings = get_settings()


def retrieve(query: str, top_k: int = 4) -> list[dict]:
    """
    Retrieve top-k FAQ documents using cosine similarity + MMR re-ranking.
    Fetches top_k * 3 candidates first, then applies MMR to select
    top_k diverse results — prevents the LLM receiving near-duplicate context.
    """
    client = get_chroma_client()
    ef = get_embedding_function()
    collection = client.get_collection(settings.chroma_collection_name, embedding_function=ef)

    total = collection.count()
    if total == 0:
        return []

    fetch_k = min(top_k * 3, total)
    results = collection.query(
        query_texts=[query],
        n_results=fetch_k,
        include=["documents", "metadatas", "distances", "embeddings"],
    )

    candidates = list(zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0],
        results["embeddings"][0],
    ))

    selected = _mmr_select(candidates, top_k=top_k, lambda_mult=0.6)
    return [{"document": doc, "metadata": meta, "distance": dist} for doc, meta, dist, _ in selected]


def _mmr_select(candidates: list[tuple], top_k: int, lambda_mult: float = 0.6) -> list[tuple]:
    """
    Maximal Marginal Relevance: balance relevance vs diversity.
    lambda_mult=1.0 → pure similarity; 0.0 → pure diversity; 0.6 → slightly relevance-biased.
    """
    if not candidates or top_k <= 0:
        return []

    selected = []
    remaining = list(candidates)
    remaining.sort(key=lambda x: x[2])  # sort by distance ascending (most relevant first)
    selected.append(remaining.pop(0))

    while len(selected) < top_k and remaining:
        best_idx, best_score = None, float("-inf")
        for i, (doc, meta, dist, emb) in enumerate(remaining):
            relevance = 1.0 - dist
            max_redundancy = max(_cosine_sim(emb, sel[3]) for sel in selected)
            mmr_score = lambda_mult * relevance - (1 - lambda_mult) * max_redundancy
            if mmr_score > best_score:
                best_score = mmr_score
                best_idx = i
        selected.append(remaining.pop(best_idx))

    return selected


def _cosine_sim(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = sum(x * x for x in a) ** 0.5
    norm_b = sum(x * x for x in b) ** 0.5
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)