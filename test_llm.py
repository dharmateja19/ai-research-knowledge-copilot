from app.llm_service import generate_answer


prompt = """
What is Deep learning?

Answer in 2-3 sentences.
"""

answer = generate_answer(prompt)

print("\n--- LLM Response ---")
print(answer)