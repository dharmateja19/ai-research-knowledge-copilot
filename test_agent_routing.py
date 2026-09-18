from app.agent import run_research_agent


result = run_research_agent(
    "What is deep learning?"
)

print("ROUTE:", result["route"])
print("ANSWER:", result["answer"])
print("SOURCES:", result["sources"])


result = run_research_agent(
    "Write a Python program to reverse a string."
)

print("\nROUTE:", result["route"])
print("ANSWER:", result["answer"])
print("SOURCES:", result["sources"])