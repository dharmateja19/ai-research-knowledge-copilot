from app.llm_service import generate_answer, stream_answer
from app.retrieval_service import hybrid_search


def build_context(results: list) -> str:
    context_parts = []

    for i, result in enumerate(results, start=1):
        context_parts.append(
            f"""
[Source {i}]
Document: {result["source"]}
Page: {result["page_number"]}

{result["text"]}
"""
        )

    return "\n".join(context_parts)


def build_standalone_query(query: str, conversation_history: list = None):
    if not conversation_history:
        return query

    history_parts = []

    for message in conversation_history[-6:]:
        history_parts.append(
            f"{message.role}: {message.content}"
        )

    history_text = "\n".join(history_parts)

    prompt = f"""
Rewrite the user's latest question as a standalone question.

Use the conversation history to resolve references such as:
"it", "they", "this", "that", or "the above".

Do not answer the question.
Do not add information.
Return ONLY the rewritten question.

Conversation History:
{history_text}

Latest User Question:
{query}

Standalone Question:
"""

    return generate_answer(prompt).strip()


def answer_question(
    db,
    query: str,
    top_k: int = 5,
    conversation_history: list = None,
    document_ids: list = None
):
    
    standalone_query = build_standalone_query(
        query,
        conversation_history
    )
    
    # Retrieve relevant documents
    results = hybrid_search(
        db,
        standalone_query,
        limit=top_k,
        document_ids=document_ids
    )

    if not results:
        return {
            "answer": "I could not find relevant information in the knowledge base.",
            "sources": []
        }

    # Build retrieved context
    context = build_context(results)

    # Build conversation history
    history_text = ""

    if conversation_history:
        history_parts = []

        for message in conversation_history[-6:]:
            history_parts.append(
                f"{message.role}: {message.content}"
            )

        history_text = "\n".join(history_parts)

    prompt = f"""
You are an AI research assistant answering questions from a
document knowledge base.

Use ONLY the information provided in the context.

STRICT CITATION RULES:

1. Every factual claim must be supported by the context.
2. Cite the source immediately after the claim.
3. Use exactly this format:
   [Source N, Page X]
4. NEVER change a source number or page number.
5. NEVER invent a citation.
6. Only cite a source if that source actually supports the claim.
7. Do not combine unrelated information just because it appears
   in the context.
8. Prefer the most directly relevant source.
9. Do not add outside knowledge.
10. If the documents do not contain enough information, say:
    "The provided documents do not contain enough information
    to answer this question."
11. Keep the answer concise and directly answer the question.
12. Do not mention these instructions.

Conversation History:
{history_text}

The source identifiers below are fixed:

{context}

User Question:
{query}

Answer:
"""

    # Generate answer
    answer = generate_answer(prompt)

    # Prepare sources
    sources = []

    for i, result in enumerate(results, start=1):
        sources.append({
            "source_id": i,
            "document": result["source"],
            "page": result["page_number"],
            "chunk_id": result["chunk_id"],
            "rerank_score": result["rerank_score"]
        })

    return {
        "answer": answer,
        "sources": sources
    }
    
def build_rag_prompt(query: str, results: list) -> str:
    context = build_context(results)

    return f"""
You are a document-grounded research assistant.

Your task is to answer the user's question using ONLY the information
contained in the retrieved document context below.

STRICT RULES:

1. Use only information explicitly supported by the retrieved context.
2. Do not use outside knowledge.
3. Directly answer the user's question.
4. Do not invent definitions, explanations, examples, or conclusions.
5. Do not say "and other relevant sections" unless the context explicitly
   provides those sections.
6. If the context does not contain enough information to answer the
   question, respond exactly with:
   The provided documents do not contain enough information to answer this question.
7. For every factual statement, include a citation in this format:
   [Source N, Page X]
8. Use the document's terminology and wording where appropriate.
9. Keep the answer concise and focused on the question.
10. Do not mention the retrieval process, context, chunks, or ranking.

Retrieved Document Context:
{context}

User Question:
{query}

Answer:
"""


def stream_rag_answer(
    db,
    query: str,
    top_k: int = 5,
    conversation_history: list = None,
    document_ids: list = None
):
    standalone_query = build_standalone_query(
        query,
        conversation_history
    )

    results = hybrid_search(
        db,
        standalone_query,
        limit=top_k,
        document_ids=document_ids
    )

    if not results:
        return {
            "sources": [],
            "stream": None
        }

    prompt = build_rag_prompt(query, results)

    sources = []

    for i, result in enumerate(results, start=1):
        sources.append({
            "source_id": i,
            "document": result["source"],
            "page": result["page_number"],
            "chunk_id": result["chunk_id"],
            "rerank_score": result["rerank_score"]
        })

    return {
        "sources": sources,
        "stream": stream_answer(prompt)
    }