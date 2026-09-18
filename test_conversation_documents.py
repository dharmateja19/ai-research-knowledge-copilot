from app.database import SessionLocal
from app.conversation_service import (
    create_conversation,
    add_document_to_conversation,
    get_conversation_documents
)


db = SessionLocal()

try:

    conversation = create_conversation(
        db,
        "Deep Learning Research"
    )

    print("Conversation ID:", conversation.id)

    document_id = 2

    document = add_document_to_conversation(
        db,
        conversation.id,
        document_id
    )

    if document:
        print("Attached document:", document.filename)
    else:
        print("Document or conversation not found")

    documents = get_conversation_documents(
        db,
        conversation.id
    )

    print("\nDocuments in conversation:")

    for doc in documents:
        print(
            f"ID: {doc.id} | "
            f"Filename: {doc.filename}"
        )

finally:
    db.close()