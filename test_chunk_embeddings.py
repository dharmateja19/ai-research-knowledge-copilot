from app.database import SessionLocal
from app.embedding_pipeline import generate_chunk_embeddings


db = SessionLocal()

try:
    document_id = 1

    embeddings = generate_chunk_embeddings(
        db,
        document_id
    )

    print("Number of chunks:", len(embeddings))

    if embeddings:
        print("First chunk:")
        print(embeddings[0]["text"][:200])

        print("\nEmbedding dimensions:")
        print(len(embeddings[0]["vector"]))

        print("\nFirst 10 vector values:")
        print(embeddings[0]["vector"][:10])

finally:
    db.close()