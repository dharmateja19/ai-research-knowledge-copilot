from app.database import SessionLocal
from app.rag_service import answer_question


db = SessionLocal()

try:
    query = "What is deep learning?"

    result = answer_question(
        db,
        query
    )

    print("\n==============================")
    print("ANSWER")
    print("==============================")

    print(result["answer"])

    print("\n==============================")
    print("SOURCES")
    print("==============================")

    for source in result["sources"]:
        print(
            f"[Source {source['source_id']}] "
            f"{source['document']} - "
            f"Page {source['page']}"
        )

finally:
    db.close()