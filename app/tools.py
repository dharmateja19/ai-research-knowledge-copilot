from app.database import SessionLocal
from app.retrieval_service import hybrid_search


def search_knowledge_base(
    query: str,
    top_k: int = 5,
    document_ids: list = None
):
    db = SessionLocal()

    try:
        results = hybrid_search(
            db,
            query,
            limit=top_k,
            document_ids=document_ids
        )

        return [
            {
                "chunk_id": result["chunk_id"],
                "document": result["source"],
                "page": result["page_number"],
                "text": result["text"],
                "score": result["rerank_score"],
            }
            for result in results
        ]

    finally:
        db.close()