from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct


QDRANT_URL = "http://localhost:6333"

COLLECTION_NAME = "document_chunks"

client = QdrantClient(
    url=QDRANT_URL
)


def create_collection():
    collections = client.get_collections()

    existing_collections = [
        collection.name
        for collection in collections.collections
    ]

    if COLLECTION_NAME not in existing_collections:
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(
                size=384,
                distance=Distance.COSINE
            )
        )

        print(f"Created collection: {COLLECTION_NAME}")

    else:
        print(f"Collection already exists: {COLLECTION_NAME}")


def insert_embeddings(embeddings):
    points = []

    for item in embeddings:
        point = PointStruct(
            id=item["chunk_id"],
            vector=item["vector"],
            payload={
                "document_id": item["document_id"],
                "chunk_id": item["chunk_id"],
                "chunk_index": item["chunk_index"],
                "page_number": item["page_number"],
                "source": item["source"],
                "text": item["text"]
            }
        )

        points.append(point)

    if points:
        client.upsert(
            collection_name=COLLECTION_NAME,
            points=points
        )

    return len(points)


def search_similar_chunks(
    query_vector,
    limit=5,
    document_ids=None
):
    query_filter = None

    if document_ids:
        from qdrant_client.models import Filter, FieldCondition, MatchAny

        query_filter = Filter(
            must=[
                FieldCondition(
                    key="document_id",
                    match=MatchAny(
                        any=document_ids
                    )
                )
            ]
        )

    results = client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_vector,
        query_filter=query_filter,
        limit=limit,
        with_payload=True
    )

    return results.points