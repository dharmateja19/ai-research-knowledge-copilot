from ollama import chat


MODEL_NAME = "llama3.2"


def generate_answer(prompt: str) -> str:
    response = chat(
        model=MODEL_NAME,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response["message"]["content"]


def stream_answer(prompt: str):
    stream = chat(
        model=MODEL_NAME,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        stream=True
    )

    for chunk in stream:
        content = chunk["message"]["content"]

        if content:
            yield content