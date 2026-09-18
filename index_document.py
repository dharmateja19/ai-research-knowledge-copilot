from app.database import SessionLocal
from app.embedding_pipeline import generate_chunk_embeddings
from app.qdrant_service import create_collection, insert_embeddings


DOCUMENT_ID = 2


db = SessionLocal()

try:
    create_collection()

    embeddings = generate_chunk_embeddings(
        db,
        DOCUMENT_ID
    )

    count = insert_embeddings(embeddings)

    print(f"Indexed {count} chunks into Qdrant.")

finally:
    db.close()