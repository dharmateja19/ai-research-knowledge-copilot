from app.database import SessionLocal
from app.conversation_service import (
    create_conversation,
    add_message,
    get_conversation_messages
)


db = SessionLocal()

try:
    conversation = create_conversation(
        db,
        "Machine Learning Discussion"
    )

    print("Conversation ID:", conversation.id)

    add_message(
        db,
        conversation.id,
        "user",
        "What is machine learning?"
    )

    add_message(
        db,
        conversation.id,
        "assistant",
        "Machine learning is a subfield of artificial intelligence."
    )

    messages = get_conversation_messages(
        db,
        conversation.id
    )

    print("\n--- Conversation ---")

    for message in messages:
        print(f"{message.role}: {message.content}")

finally:
    db.close()