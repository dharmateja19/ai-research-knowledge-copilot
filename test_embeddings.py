from app.embedding_service import generate_embedding


text = "Machine learning allows computers to learn from data."

embedding = generate_embedding(text)

print("Embedding dimensions:", len(embedding))
print("First 10 values:", embedding[:10])