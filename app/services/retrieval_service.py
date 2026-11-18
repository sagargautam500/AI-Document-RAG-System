
from app.services.qdrant_service import (
    get_client,
    COLLECTION_NAME
)

from app.services.embedding_service import generate_embeddings


def search_similar_chunks(
    query: str,
    limit: int = 5
) -> list[dict]:
    """
    Search for relevant document chunks in Qdrant.
    """

    if not query.strip():
        raise ValueError("Search query cannot be empty.")

    # Step 1: Convert user query into embedding
    query_embedding = generate_embeddings([query])[0]

    # Step 2: Get Qdrant client
    client = get_client()

    # Step 3: Search similar vectors
    search_results = client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_embedding,
        limit=limit,
        with_payload=True
    )

    # Step 4: Extract relevant information
    results = []

    for point in search_results.points:
        results.append({
            "score": point.score,
            "document_id": point.payload.get("document_id"),
            "filename": point.payload.get("filename"),
            "chunk_id": point.payload.get("chunk_id"),
            "text": point.payload.get("text")
        })

    return results
