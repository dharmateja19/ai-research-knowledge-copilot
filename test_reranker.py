from app.database import SessionLocal
from app.retrieval_service import hybrid_search


db = SessionLocal()

try:
    query = "What is machine learning?"

    results = hybrid_search(
        db,
        query,
        limit=5
    )

    for i, result in enumerate(results, start=1):
        print(f"\n--- Final Result {i} ---")
        print("Rerank score:", result["rerank_score"])
        print("Hybrid score:", result["hybrid_score"])
        print("Semantic score:", result["semantic_score"])
        print("Keyword score:", result["keyword_score"])
        print("Page:", result["page_number"])
        print("Chunk ID:", result["chunk_id"])
        print("Text:")
        print(result["text"][:500])

finally:
    db.close()