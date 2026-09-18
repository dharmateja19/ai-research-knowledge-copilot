from sqlalchemy.orm import Session

from app.models import DocumentChunk
from app.embedding_service import generate_embedding


def generate_chunk_embeddings(db: Session, document_id: int):
    chunks = (
        db.query(DocumentChunk)
        .filter(DocumentChunk.document_id == document_id)
        .order_by(DocumentChunk.chunk_index)
        .all()
    )

    embeddings = []

    for chunk in chunks:
        vector = generate_embedding(chunk.text)

        embeddings.append({
            "chunk_id": chunk.id,
            "document_id": chunk.document_id,
            "chunk_index": chunk.chunk_index,
            "page_number": chunk.page_number,
            "source": chunk.source,
            "text": chunk.text,
            "vector": vector
        })

    return embeddings