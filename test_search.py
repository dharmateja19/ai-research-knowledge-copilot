from app.retrieval_service import search_documents


query = "What is machine learning?"

results = search_documents(
    query,
    limit=5
)

for i, result in enumerate(results, start=1):

    print(f"\n--- Result {i} ---")
    print("Score:", result["score"])
    print("Source:", result["source"])
    print("Page:", result["page_number"])
    print("Chunk ID:", result["chunk_id"])
    print("Text:")
    print(result["text"][:500])