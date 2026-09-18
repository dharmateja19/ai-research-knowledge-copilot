from app.database import SessionLocal
from app.retrieval_service import hybrid_search


db = SessionLocal()

try:
    results = hybrid_search(
        db,
        "What is deep learning?",
        limit=5,
        document_ids=[2]
    )

    print("\nRESULTS:\n")

    for result in results:
        print(
            f"Document ID: {result['document_id']} | "
            f"Page: {result['page_number']} | "
            f"Score: {result['rerank_score']}"
        )

finally:
    db.close()