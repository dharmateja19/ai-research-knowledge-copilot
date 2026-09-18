from sqlalchemy.orm import Session

from app.embedding_service import generate_embedding
from app.qdrant_service import search_similar_chunks
from app.keyword_search import keyword_search
from app.reranker_service import rerank_results


def hybrid_search(
    db: Session,
    query: str,
    limit: int = 10,
    document_ids=None
):
    query_vector = generate_embedding(query)

    semantic_results = search_similar_chunks(
        query_vector,
        limit=limit,
        document_ids=document_ids
    )

    keyword_results = keyword_search(
        db,
        query,
        limit=limit,
        document_ids=document_ids
    )

    combined = {}

    for result in semantic_results:
        chunk_id = result.payload["chunk_id"]

        combined[chunk_id] = {
            "chunk_id": chunk_id,
            "document_id": result.payload["document_id"],
            "page_number": result.payload["page_number"],
            "source": result.payload["source"],
            "text": result.payload["text"],
            "semantic_score": result.score,
            "keyword_score": 0.0
        }

    for result in keyword_results:
        chunk_id = result["chunk_id"]

        if chunk_id not in combined:
            combined[chunk_id] = {
                "chunk_id": chunk_id,
                "document_id": result["document_id"],
                "page_number": result["page_number"],
                "source": result["source"],
                "text": result["text"],
                "semantic_score": 0.0,
                "keyword_score": result["keyword_score"]
            }

        else:
            combined[chunk_id]["keyword_score"] = (
                result["keyword_score"]
            )

    for result in combined.values():
        result["hybrid_score"] = (
            0.7 * result["semantic_score"]
            + 0.3 * result["keyword_score"]
        )

    hybrid_results = sorted(
        combined.values(),
        key=lambda x: x["hybrid_score"],
        reverse=True
    )

    hybrid_results = hybrid_results[:10]

    return rerank_results(
        query,
        hybrid_results,
        top_k=limit
    )