from app.agent import research_graph


questions = [
    "What is deep learning?",
    "Write a Python program to reverse a string."
]


for question in questions:

    print("\n==============================")
    print("QUESTION")
    print("==============================")
    print(question)

    result = research_graph.invoke({
        "question": question,
        "route": "",
        "retrieved_context": "",
        "answer": "",
        "sources": []
    })

    print("\nROUTE:")
    print(result["route"])

    print("\nANSWER:")
    print(result["answer"])

    print("\nSOURCES:")

    for source in result["sources"]:
        print(
            f"[Source {source['source_id']}] "
            f"{source['document']} - "
            f"Page {source['page']}"
        )