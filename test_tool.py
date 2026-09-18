from app.tools import search_knowledge_base


results = search_knowledge_base("What is deep learning?", top_k=3)

for i, result in enumerate(results, start=1):
    print("\n==============================")
    print(f"RESULT {i}")
    print("==============================")
    print("Document:", result["document"])
    print("Page:", result["page"])
    print("Score:", result["score"])
    print("Text:")
    print(result["text"][:500])