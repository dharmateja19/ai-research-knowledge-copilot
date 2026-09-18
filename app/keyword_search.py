import re

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models import DocumentChunk


STOP_WORDS = {
    "what",
    "is",
    "are",
    "the",
    "a",
    "an",
    "of",
    "in",
    "on",
    "to",
    "and",
    "for",
    "how",
    "why",
    "does",
    "do",
    "was",
    "were",
}


def keyword_search(
    db: Session,
    query: str,
    limit: int = 10,
    document_ids=None
):
    terms = re.findall(
        r"\b\w+\b",
        query.lower()
    )

    terms = [
        term
        for term in terms
        if term not in STOP_WORDS
    ]

    if not terms:
        return []

    # Search for chunks containing ANY query term
    filters = [
        DocumentChunk.text.ilike(f"%{term}%")
        for term in terms
    ]

    query_builder = (
        db.query(DocumentChunk)
        .filter(or_(*filters))
    )

    # Restrict search to selected documents
    if document_ids:
        query_builder = query_builder.filter(
            DocumentChunk.document_id.in_(document_ids)
        )

    chunks = query_builder.all()

    results = []

    for chunk in chunks:

        text_lower = chunk.text.lower()

        matched_terms = sum(
            1
            for term in terms
            if term in text_lower
        )

        keyword_score = (
            matched_terms / len(terms)
        )

        results.append({
            "chunk_id": chunk.id,
            "document_id": chunk.document_id,
            "chunk_index": chunk.chunk_index,
            "page_number": chunk.page_number,
            "source": chunk.source,
            "text": chunk.text,
            "keyword_score": keyword_score
        })

    results.sort(
        key=lambda x: x["keyword_score"],
        reverse=True
    )

    return results[:limit]