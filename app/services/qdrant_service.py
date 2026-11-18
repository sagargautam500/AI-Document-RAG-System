
from uuid import uuid4
from functools import lru_cache

from qdrant_client import QdrantClient, models


COLLECTION_NAME = "documents"
VECTOR_SIZE = 384


@lru_cache(maxsize=1)
def get_client() -> QdrantClient:
    """Create the local Qdrant client only when it is first needed."""
    return QdrantClient(path="./qdrant_storage")


def create_collection() -> None:
    """Create the collection if it does not already exist."""

    client = get_client()
    if not client.collection_exists(COLLECTION_NAME):

        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=models.VectorParams(
                size=VECTOR_SIZE,
                distance=models.Distance.COSINE
            )
        )


def store_chunks(
    document_id: str,
    filename: str,
    chunks: list[str],
    embeddings: list[list[float]],
    chunking_strategy: str
) -> int:
    """Store document chunks and embeddings in Qdrant."""

    if len(chunks) != len(embeddings):
        raise ValueError(
            "Number of chunks and embeddings must be equal."
        )

    create_collection()

    points = []

    for index, (chunk, embedding) in enumerate(
        zip(chunks, embeddings)
    ):

        point = models.PointStruct(
            id=str(uuid4()),
            vector=embedding,
            payload={
                "document_id": document_id,
                "filename": filename,
                "chunk_id": index,
                "text": chunk,
                "chunking_strategy": chunking_strategy
            }
        )

        points.append(point)

    if points:
        get_client().upsert(
            collection_name=COLLECTION_NAME,
            points=points
        )

    return len(points)
