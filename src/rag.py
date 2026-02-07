"""
RAG pipeline: chunk documents, generate embeddings, store in vector index, retrieve top-k.
Uses OpenAI embeddings and a local vector store (FAISS or in-memory).
"""
from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

from src.data import load_faq_documents

# Chunking
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50


def _get_embedding_client(api_key: str):
    """Lazy import openai and return embedding-capable client."""
    try:
        from openai import OpenAI
        return OpenAI(api_key=api_key)
    except Exception as e:
        raise RuntimeError(f"OpenAI client unavailable: {e}") from e


def _chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    """Simple sentence-aware chunking."""
    words = text.replace("\n", " ").split()
    chunks = []
    start = 0
    while start < len(words):
        end = min(start + chunk_size, len(words))
        chunk = " ".join(words[start:end])
        if chunk.strip():
            chunks.append(chunk.strip())
        start = end - overlap if end < len(words) else len(words)
    return chunks if chunks else [text[:chunk_size]]


def build_documents_for_rag(
    faq_path: Path | None = None,
    docs_dir: Path | None = None,
) -> list[dict[str, Any]]:
    """
    Load FAQ docs and split into chunks. Each item: {id, text, source, chunk_idx}.
    """
    raw = load_faq_documents(faq_path=faq_path, docs_dir=docs_dir)
    out = []
    for doc in raw:
        doc_id = doc["id"]
        text = doc["text"]
        source = doc["source"]
        for i, chunk in enumerate(_chunk_text(text)):
            chunk_id = hashlib.md5(f"{doc_id}_{i}_{chunk[:50]}".encode()).hexdigest()[:12]
            out.append({
                "id": f"{doc_id}_{chunk_id}",
                "text": chunk,
                "source": source,
                "doc_id": doc_id,
                "chunk_idx": i,
            })
    return out


def get_embedding(text: str, client: Any, model: str = "text-embedding-3-small") -> list[float]:
    """Single text to embedding vector."""
    r = client.embeddings.create(input=[text], model=model)
    return r.data[0].embedding


def build_index(chunks: list[dict], api_key: str, model: str = "text-embedding-3-small"):
    """
    Build vector index from chunks. Returns (index, chunk_list, embeddings_list).
    Uses numpy for storage if faiss not available.
    """
    client = _get_embedding_client(api_key)
    texts = [c["text"] for c in chunks]
    embeddings = []
    batch_size = 100
    for i in range(0, len(texts), batch_size):
        batch = texts[i : i + batch_size]
        r = client.embeddings.create(input=batch, model=model)
        for d in r.data:
            embeddings.append(d.embedding)
    import numpy as np
    emb_matrix = np.array(embeddings).astype("float32")
    try:
        import faiss
        dim = emb_matrix.shape[1]
        index = faiss.IndexFlatL2(dim)
        index.add(emb_matrix)
        return index, chunks, emb_matrix
    except ImportError:
        # Fallback: store embeddings and use brute-force L2 in numpy
        return None, chunks, emb_matrix


def retrieve(
    query: str,
    api_key: str,
    index_or_embeddings: Any,
    chunks: list[dict],
    k: int = 5,
    use_faiss: bool = True,
    model: str = "text-embedding-3-small",
) -> list[tuple[dict, float]]:
    """
    Retrieve top-k chunks. index_or_embeddings is either faiss.Index or numpy matrix.
    Returns list of (chunk_dict, distance).
    """
    client = _get_embedding_client(api_key)
    q_emb = get_embedding(query, client, model=model)
    import numpy as np
    q = np.array([q_emb], dtype="float32")
    if use_faiss and hasattr(index_or_embeddings, "search"):
        D, I = index_or_embeddings.search(q, min(k, len(chunks)))
        return [(chunks[i], float(D[0][j])) for j, i in enumerate(I[0])]
    # Brute-force
    emb_matrix = index_or_embeddings
    d = np.sqrt(((emb_matrix - q) ** 2).sum(axis=1))
    idx = np.argsort(d)[:k]
    return [(chunks[i], float(d[i])) for i in idx]
